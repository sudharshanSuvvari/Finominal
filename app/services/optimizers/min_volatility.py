import numpy as np

from app.services.optimizers.base import BaseOptimizer
from app.utils.common import (
    portfolio_volatility,
)

class MinVolatilityOptimizer(
    BaseOptimizer
):

    def objective(
        self,
        weights: np.ndarray,
        cov_matrix: np.ndarray,
    ) -> float:

        return portfolio_volatility(
            weights,
            cov_matrix,
        )