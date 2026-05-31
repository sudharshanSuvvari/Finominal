import numpy as np

from app.services.optimizers.base import BaseOptimizer
from app.utils.common import risk_contributions


class RiskParityOptimizer(BaseOptimizer):
    """
    Minimises the sum of squared deviations between each asset's risk
    contribution and the equal-risk target (1/n).
    """

    def get_objective_args(self, returns_df) -> tuple:
        cov_matrix = returns_df.cov().values
        return (cov_matrix,)

    def objective(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        rc = risk_contributions(weights, cov_matrix)
        risk_budget = rc / np.sum(rc)
        target_budget = np.ones(len(weights)) / len(weights)
        return np.sum((risk_budget - target_budget) ** 2)