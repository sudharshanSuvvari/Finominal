import numpy as np
import pandas as pd


def portfolio_returns(
    weights: np.ndarray,
    returns_df: pd.DataFrame,
) -> pd.Series:
    return returns_df.dot(weights)

def covariance_matrix(
    returns_df: pd.DataFrame,
) -> pd.DataFrame:
    return returns_df.cov()

def portfolio_volatility(
    weights: np.ndarray,
    cov_matrix: pd.DataFrame,
) -> float:

    return np.sqrt(
        weights.T @ cov_matrix @ weights
    )

def portfolio_cagr(
    portfolio_returns: pd.Series,
) -> float:

    cumulative_growth = (
        1 + portfolio_returns
    ).prod()

    years = len(portfolio_returns) / 12

    return cumulative_growth ** (1 / years) - 1

def sharpe_ratio(
    weights,
    returns_df,
):

    mu = returns_df.mean().values
    cov = returns_df.cov().values

    portfolio_return = (
        weights @ mu
    )

    portfolio_volatility = np.sqrt(
        weights.T @ cov @ weights
    )

    return (
        portfolio_return
        / portfolio_volatility
    )

def max_drawdown(
    weights: np.ndarray,
    returns_df: pd.DataFrame,
) -> float:

    port_returns = portfolio_returns(
        weights,
        returns_df,
    )

    cumulative = (
        1 + port_returns
    ).cumprod()

    running_max = cumulative.cummax()

    drawdowns = (
        cumulative - running_max
    ) / running_max

    return drawdowns.min()


def get_weight_constraints(
    dividend_yields=None,
    min_dividend_yield=None,
):
    constraints = [
        {
            "type": "eq",
            "fun": lambda w:
                np.sum(w) - 1,
        }
    ]

    if (
        dividend_yields is not None
        and min_dividend_yield is not None
    ):
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w:
                    np.dot(
                        w,
                        dividend_yields,
                    )
                    - min_dividend_yield,
            }
        )

    return constraints


def get_bounds(
    n_assets: int,
    min_weight: float | None,
    max_weight: float | None,
):
    return [
        (
            min_weight if min_weight is not None else 0,
            max_weight if max_weight is not None else 1,
        )
        for _ in range(n_assets)
    ]

def get_initial_weights(
    n_assets: int,
):
    return np.ones(
        n_assets
    ) / n_assets


def risk_contributions(
    weights: np.ndarray,
    cov_matrix: np.ndarray,
) -> np.ndarray:

    portfolio_vol = (
        portfolio_volatility(
            weights,
            cov_matrix,
        )
    )

    marginal_risk = (
        cov_matrix @ weights
    ) / portfolio_vol

    return (
        weights
        * marginal_risk
    )