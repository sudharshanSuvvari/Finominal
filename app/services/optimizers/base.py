from abc import ABC, abstractmethod

import numpy as np
from scipy.optimize import minimize
from app.utils.common import sharpe_ratio

from app.utils.common import (
    get_initial_weights,
)

class BaseOptimizer(ABC):

    @abstractmethod
    def objective(
        self,
        weights,
        *args,
    ):
        pass

    @abstractmethod
    def get_objective_args(
        self,
        returns_df,
    ):
        pass

    def optimize(
        self,
        returns_df,
        bounds=None,
        constraints=None,
    ):

        args = self.get_objective_args(
            returns_df
        )

        result = minimize(
            fun=self.objective,
            x0=get_initial_weights(
                len(returns_df.columns)
            ),
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        print(
            "optimized sharpe",
            sharpe_ratio(
                result.x,
                returns_df,
            )
        )

        print(result.x)
        return result.x