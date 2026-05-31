from app.services.optimizers.base import BaseOptimizer

from app.utils.common import sharpe_ratio

class MaxSharpeOptimizer(
    BaseOptimizer
):

    def get_objective_args(
        self,
        returns_df,
    ):
        return (
            returns_df,
        )

    def objective(
        self,
        weights,
        returns_df,
    ):
        return -sharpe_ratio(
            weights,
            returns_df,
        )