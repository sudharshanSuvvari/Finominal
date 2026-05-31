"""
app/services/optimizers/min_drawdown.py

Minimises the maximum historical drawdown of the portfolio.

Approach
--------
scipy.minimize is a gradient-based solver; max-drawdown is neither convex
nor differentiable (it depends on the order of returns).  We handle this
with two complementary techniques:

1. We negate the drawdown value (which is already negative, so the objective
   returns a positive number that the solver minimises toward zero).

2. We add multiple random restarts (n_restarts) and return the weights from
   the run with the lowest drawdown.  This guards against the solver getting
   trapped in a poor local minimum — the most common reason for variable
   outputs on path-dependent objectives.
"""

import numpy as np
from scipy.optimize import minimize

from app.services.optimizers.base import BaseOptimizer
from app.utils.common import (
    get_initial_weights,
    max_drawdown,
    sharpe_ratio,
)


class MinDrawdownOptimizer(BaseOptimizer):
    """
    Parameters
    ----------
    n_restarts : int
        Number of random starting-weight vectors to try in addition to the
        equal-weight start.  Higher values improve reliability at the cost
        of runtime.  Default 10 is sufficient for 5-asset portfolios.
    seed : int | None
        Random seed for reproducibility across runs.
    """

    def __init__(self, n_restarts: int = 10, seed: int | None = 42):
        self.n_restarts = n_restarts
        self.seed = seed

    # ------------------------------------------------------------------
    # BaseOptimizer interface
    # ------------------------------------------------------------------

    def get_objective_args(self, returns_df) -> tuple:
        # Pass the full returns DataFrame; max_drawdown derives the path
        # series itself so we need the per-period returns, not just cov.
        return (returns_df,)

    def objective(self, weights: np.ndarray, returns_df) -> float:
        # max_drawdown() returns a negative number (e.g. -0.35 for -35 %).
        # Negating it gives a positive value; the solver drives this to 0.
        return -max_drawdown(weights, returns_df)

    # ------------------------------------------------------------------
    # Override optimize() to add random restarts
    # ------------------------------------------------------------------

    def optimize(
        self,
        returns_df,
        bounds=None,
        constraints=None,
    ) -> np.ndarray:
        args = self.get_objective_args(returns_df)
        n_assets = len(returns_df.columns)

        rng = np.random.default_rng(self.seed)

        # Build a list of starting points: equal-weight + random restarts
        starting_points = [get_initial_weights(n_assets)]
        for _ in range(self.n_restarts):
            w = rng.dirichlet(np.ones(n_assets))  # random weights summing to 1
            starting_points.append(w)

        best_weights = None
        best_objective = np.inf

        for x0 in starting_points:
            result = minimize(
                fun=self.objective,
                x0=x0,
                args=args,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"ftol": 1e-12, "maxiter": 1000},
            )
            # Accept any result that improved the objective, even if the solver
            # reports convergence warnings (common with non-smooth objectives).
            if result.fun < best_objective:
                best_objective = result.fun
                best_weights = result.x

        if best_weights is None:
            raise RuntimeError("MinDrawdownOptimizer: all restarts failed.")

        print(
            f"[MinDrawdownOptimizer] "
            f"max_drawdown={-best_objective:.4f} | "
            f"annualised Sharpe={sharpe_ratio(best_weights, returns_df):.4f} | "
            f"weights={np.round(best_weights, 4)}"
        )
        return best_weights