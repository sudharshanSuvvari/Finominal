from abc import ABC, abstractmethod

import numpy as np
from scipy.optimize import minimize

from app.utils.common import get_initial_weights, sharpe_ratio


class BaseOptimizer(ABC):

    @abstractmethod
    def objective(self, weights: np.ndarray, *args) -> float:
        pass

    @abstractmethod
    def get_objective_args(self, returns_df) -> tuple:
        pass

    def optimize(
        self,
        returns_df,
        bounds=None,
        constraints=None,
    ) -> np.ndarray:
        args = self.get_objective_args(returns_df)
        n_assets = len(returns_df.columns)

        result = minimize(
            fun=self.objective,
            x0=get_initial_weights(n_assets),
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"ftol": 1e-12, "maxiter": 1000},
        )

        if not result.success:
            raise RuntimeError(
                f"{self.__class__.__name__} optimisation failed: {result.message}"
            )

        weights = result.x
        print(
            f"[{self.__class__.__name__}] "
            f"annualised Sharpe={sharpe_ratio(weights, returns_df):.4f} | "
            f"weights={np.round(weights, 4)}"
        )
        return weights