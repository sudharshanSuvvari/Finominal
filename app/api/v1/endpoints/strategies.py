"""
app/api/v1/endpoints/strategies.py

POST /strategies/optimize

All Pydantic validation (weight sums, constraint feasibility, valid strategy
names) happens in OptimizationRequest before this function runs, so the router
only needs to handle runtime errors (bad data, solver failures, missing tickers).
"""

import numpy as np
from fastapi import APIRouter, HTTPException

from app.schemas.strategies import OptimizationRequest
from app.core.state import app_state
from app.services.equal import equal_weights as compute_equal_weights
from app.services.optimizers.max_sharpe import MaxSharpeOptimizer
from app.services.optimizers.min_drawdown import MinDrawdownOptimizer
from app.services.optimizers.min_volatility import MinVolatilityOptimizer
from app.services.optimizers.risk_parity import RiskParityOptimizer
from app.utils.common import get_bounds, get_weight_constraints, sharpe_ratio
from app.utils.helpers import build_allocation_changes

strategies_router = APIRouter()


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def _build_selected_returns(holdings, returns_df):
    """
    Pivot the global returns DataFrame down to only the requested tickers,
    dropping any rows with NaN so all strategies see a complete matrix.
    Raises HTTPException 400 if any ticker has no data at all.
    """
    tickers = [str(h.ticker) for h in holdings]
    missing = [t for t in tickers if t not in returns_df["ticker"].values]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"No return data found for ticker(s): {missing}. "
                   "Check that the tickers match the loaded dataset.",
        )

    filtered = returns_df.loc[returns_df["ticker"].isin(tickers)].copy()
    selected = filtered.pivot(
        index="date",
        columns="ticker",
        values="total_return",
    ).dropna()

    if selected.empty:
        raise HTTPException(
            status_code=400,
            detail=(
                "After aligning dates, no overlapping return observations remain. "
                "Ensure the requested tickers share a common history."
            ),
        )
    return selected


def _build_bounds(constraints, n_assets: int):
    return get_bounds(
        n_assets=n_assets,
        min_weight=(constraints.min_weight / 100 if constraints and constraints.min_weight is not None else None),
        max_weight=(constraints.max_weight / 100 if constraints and constraints.max_weight is not None else None),
    )


def _build_optimizer_constraints(constraints, selected_returns):
    """
    Build the scipy constraint list.  Handles missing dividend yield data
    gracefully instead of raising a raw KeyError.
    """
    dividend_yields = app_state.DIVIDEND_YIELDS

    # Validate that every ticker has a yield on record before building the array
    missing_yields = [
        t for t in selected_returns.columns
        if t not in dividend_yields
    ]
    if missing_yields:
        raise HTTPException(
            status_code=400,
            detail=f"Dividend yield data missing for ticker(s): {missing_yields}.",
        )

    ordered_yields = np.array(
        [dividend_yields[ticker] for ticker in selected_returns.columns]
    )

    return get_weight_constraints(
        dividend_yields=ordered_yields,
        min_dividend_yield=(
            constraints.min_dividend_yield / 100
            if constraints and constraints.min_dividend_yield is not None
            else None
        ),
    )


def _run_optimizer(optimizer, selected_returns, bounds, optimizer_constraints):
    """
    Wraps optimizer.optimize() and converts RuntimeError (solver failure /
    infeasible constraints) into a clean 422 HTTP response.
    """
    try:
        return optimizer.optimize(
            returns_df=selected_returns,
            bounds=bounds,
            constraints=optimizer_constraints,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Optimisation failed: {exc}. "
                "This usually means the constraint set is infeasible "
                "(e.g. min_dividend_yield is too high for the selected securities)."
            ),
        )


def _build_response(strategy: str, holdings, selected_returns, optimized_weights):
    """
    Shared response builder — calls helpers.build_allocation_changes and
    wraps any ValueError (e.g. unknown ticker in securities_df) as a 400.
    """
    try:
        allocation_changes = build_allocation_changes(
            holdings=holdings,
            selected_returns=selected_returns,
            optimized_weights=optimized_weights,
            securities_df=app_state.securities_df,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "optimization_strategy": strategy,
        "allocation_changes": allocation_changes,
    }


# ------------------------------------------------------------------ #
# Endpoint                                                             #
# ------------------------------------------------------------------ #

@strategies_router.post("/optimize")
def optimize_portfolio(request: OptimizationRequest):
    """
    Optimise a portfolio using the requested strategy and return allocation changes.

    Supported strategies

    equal_weights       : trivial 1/n baseline.

    risk_parity         : equal risk contribution per asset.

    minimize_drawdown   : minimise maximum historical drawdown.

    minimize_volatility : minimise portfolio standard deviation.

    maximize_sharpe     : maximise annualised Sharpe ratio (rf = 0).
    """
    strategy = request.strategy
    holdings = request.holdings
    constraints = request.constraints

    returns_df = app_state.returns_df
    selected_returns = _build_selected_returns(holdings, returns_df)

    n_assets = len(selected_returns.columns)
    bounds = _build_bounds(constraints, n_assets)
    optimizer_constraints = _build_optimizer_constraints(constraints, selected_returns)

    # ------------------------------------------------------------------ #
    # equal_weights — no optimiser  #
    # ------------------------------------------------------------------ #
    if strategy == "equal_weights":
        # compute_equal_weights returns a weight array already in [0,1] fractions
        optimized_weights = compute_equal_weights(holdings=holdings)
        return _build_response(strategy, holdings, selected_returns, optimized_weights)

    # ------------------------------------------------------------------ #
    # Solver-based strategies                                             #
    # ------------------------------------------------------------------ #
    optimizer_map = {
        "risk_parity": RiskParityOptimizer(),
        "minimize_drawdown": MinDrawdownOptimizer(),
        "minimize_volatility": MinVolatilityOptimizer(),
        "maximize_sharpe": MaxSharpeOptimizer(),
    }

    optimizer = optimizer_map[strategy]

    # logging equal-weight Sharpe for Sharpe-based strategies
    if strategy == "maximize_sharpe":
        equal_w = np.ones(n_assets) / n_assets
        print(
            f"[maximize_sharpe] equal-weight Sharpe="
            f"{sharpe_ratio(equal_w, selected_returns):.4f}"
        )

    optimized_weights = _run_optimizer(
        optimizer, selected_returns, bounds, optimizer_constraints
    )

    return _build_response(strategy, holdings, selected_returns, optimized_weights)