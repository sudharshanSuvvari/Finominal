from app.services.optimizers.base import BaseOptimizer
from app.utils.common import sharpe_ratio


class MaxSharpeOptimizer(BaseOptimizer):
    """
    Maximises the annualised Sharpe ratio (risk-free rate = 0).

    """

    def get_objective_args(self, returns_df) -> tuple:
        return (returns_df,)

    def objective(self, weights, returns_df) -> float:
        return -sharpe_ratio(weights, returns_df)