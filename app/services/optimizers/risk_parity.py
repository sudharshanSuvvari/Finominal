import numpy as np

from app.services.optimizers.base import BaseOptimizer

from app.utils.common import risk_contributions


class RiskParityOptimizer(
    BaseOptimizer
):

    def get_objective_args(
        self,
        returns_df,
    ):
        return (
            returns_df.cov().values,
        )

    def objective(
        self,
        weights,
        cov_matrix,
    ):

        rc = risk_contributions(
            weights,
            cov_matrix,
        )

        risk_budget = (
            rc / np.sum(rc)
        )

        target_budget = (
            np.ones(len(weights))
            / len(weights)
        )

        return np.sum(
            (
                risk_budget
                - target_budget
            ) ** 2
        )   