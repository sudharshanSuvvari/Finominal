import numpy as np

from app.services.optimizers.base import BaseOptimizer
from app.utils.common import portfolio_volatility


class MinVolatilityOptimizer(BaseOptimizer):
    """
    Minimises annualised portfolio volatility.

    """

    def get_objective_args(self, returns_df) -> tuple:
        cov_matrix = returns_df.cov().values
        return (cov_matrix,)

    def objective(self, weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        return portfolio_volatility(weights, cov_matrix)