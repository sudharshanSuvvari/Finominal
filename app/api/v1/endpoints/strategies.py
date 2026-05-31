from app.services.optimizers.max_sharpe import MaxSharpeOptimizer
from app.services.optimizers.risk_parity import RiskParityOptimizer
from app.utils.common import get_weight_constraints, risk_contributions, risk_contributions, sharpe_ratio
from fastapi import APIRouter

import numpy as np
import pandas as pd

from app.schemas.strategies import OptimizationRequest
from app.core.state import app_state

from app.services.equal import equal_weights
from app.services.optimizers.min_volatility import MinVolatilityOptimizer
from app.utils.helpers import build_allocation_changes

from app.utils.common import get_bounds
strategies_router = APIRouter()

@strategies_router.post("/optimize")
def optimize_portfolio(
    request: OptimizationRequest,
):
    strategy = request.strategy
    holdings = request.holdings
    constraints = request.constraints

    tickers = [str(h.ticker) for h in holdings]   
    returns_df = app_state.returns_df

    filtered_df = returns_df.loc[returns_df["ticker"].isin(tickers)].copy()
    selected_returns = filtered_df.pivot(
                index="date",
                columns="ticker",
                values="total_return",
        )
    
    selected_returns = selected_returns.dropna()
    

    # Apply bounds 
    bounds = get_bounds(
        n_assets=len(selected_returns.columns),
        min_weight=(
            (constraints.min_weight/100)
            if constraints
            else None
        ),
        max_weight=(
            (constraints.max_weight/100)
            if constraints
            else None
        ),
    )
    
    print("Bounds:", bounds)

    dividend_yields = app_state.DIVIDEND_YIELDS

    # Apply constraints to the optimization process
    ordered_dividend_yields = np.array(
        [
            dividend_yields[
                ticker
            ]
            for ticker in selected_returns.columns
        ]
    )

    optimizer_constraints = get_weight_constraints(
        dividend_yields=ordered_dividend_yields,
        min_dividend_yield=(
            (constraints.min_dividend_yield/100)
            if constraints
            else None
        ),
    )

    # Placeholder for optimization logic based on the selected strategy
    if strategy == "equal_weights":

        result = equal_weights(
            holdings=holdings,
        )
        
        return {"weights": result.tolist()}
    
    elif strategy == "minimize_volatility":
        optimizer = MinVolatilityOptimizer()

        cov_matrix = (
            selected_returns.cov().values
        )

        optimized_weights = optimizer.optimize(
            returns_df=selected_returns,
            cov_matrix=cov_matrix,
            bounds=bounds,
            constraints=optimizer_constraints,
        )
        

        allocation_changes = build_allocation_changes(
            holdings=holdings,
            optimized_weights=optimized_weights,
            securities_df=app_state.securities_df,
        )

        return {
            "optimization_strategy": strategy,
            "allocation_changes": allocation_changes,
        }
    
    elif strategy == "maximize_sharpe":
        
        optimizer = MaxSharpeOptimizer()

        equal_weights = np.ones(len(selected_returns.columns)) / len(selected_returns.columns)

        print(
            "equal sharpe",
            sharpe_ratio(
                equal_weights,
                selected_returns,
            )
        )

        optimized_weights = optimizer.optimize(
            returns_df=selected_returns,
            bounds=bounds,
            constraints=optimizer_constraints,
        )

        allocation_changes = build_allocation_changes(
            holdings=holdings,
            selected_returns=selected_returns,
            optimized_weights=optimized_weights,
            securities_df=app_state.securities_df,
        )

        return {
            "optimization_strategy": strategy,
            "allocation_changes": allocation_changes,
        }
    
    elif strategy == "risk_parity":

        optimizer = (
            RiskParityOptimizer()
        )

        optimized_weights = optimizer.optimize(
            selected_returns,
            bounds=bounds,
            constraints=optimizer_constraints,
        )
        
        allocation_changes = build_allocation_changes(
            holdings=holdings,
            selected_returns=selected_returns,
            optimized_weights=optimized_weights,
            securities_df=app_state.securities_df,
        )

        return {
            "optimization_strategy": strategy,
            "allocation_changes": allocation_changes,
        }
    else:
        raise ValueError("Unsupported strategy selected")
    