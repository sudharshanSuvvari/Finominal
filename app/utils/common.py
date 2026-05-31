import numpy as np
import pandas as pd

ANNUALIZATION_FACTOR = 12  # monthly data → annualize by ×12 / √12


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
    cov_matrix: np.ndarray | pd.DataFrame,
) -> float:
    return np.sqrt(weights.T @ cov_matrix @ weights)


def portfolio_cagr(
    portfolio_returns: pd.Series,
) -> float:
    cumulative_growth = (1 + portfolio_returns).prod()
    years = len(portfolio_returns) / ANNUALIZATION_FACTOR
    return cumulative_growth ** (1 / years) - 1


def sharpe_ratio(
    weights: np.ndarray,
    returns_df: pd.DataFrame,
) -> float:
    """
    Annualised Sharpe ratio (assumes monthly return data, risk-free rate = 0).

    annualised_return = monthly_mean * 12
    annualised_vol    = monthly_vol  * sqrt(12)
    sharpe            = annualised_return / annualised_vol
                      = (monthly_mean / monthly_vol) * sqrt(12)
    """
    mu = returns_df.mean().values
    cov = returns_df.cov().values

    port_return = weights @ mu
    port_vol = np.sqrt(weights.T @ cov @ weights)

    if port_vol == 0:
        return 0.0

    # annualise: multiply by sqrt(12) — constant factor preserves optimum weights
    return (port_return / port_vol) * np.sqrt(ANNUALIZATION_FACTOR)


def max_drawdown(
    weights: np.ndarray,
    returns_df: pd.DataFrame,
) -> float:
    port_returns = portfolio_returns(weights, returns_df)
    cumulative = (1 + port_returns).cumprod()
    running_max = cumulative.cummax()
    drawdowns = (cumulative - running_max) / running_max
    return drawdowns.min()


def get_weight_constraints(
    dividend_yields: np.ndarray | None = None,
    min_dividend_yield: float | None = None,
) -> list[dict]:
    constraints: list[dict] = [
        {
            "type": "eq",
            "fun": lambda w: np.sum(w) - 1,
        }
    ]

    if dividend_yields is not None and min_dividend_yield is not None:
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda w: np.dot(w, dividend_yields) - min_dividend_yield,
            }
        )

    return constraints


def get_bounds(
    n_assets: int,
    min_weight: float | None,
    max_weight: float | None,
) -> list[tuple[float, float]]:
    return [
        (
            min_weight if min_weight is not None else 0.0,
            max_weight if max_weight is not None else 1.0,
        )
        for _ in range(n_assets)
    ]


def get_initial_weights(n_assets: int) -> np.ndarray:
    return np.ones(n_assets) / n_assets


def risk_contributions(
    weights: np.ndarray,
    cov_matrix: np.ndarray,
) -> np.ndarray:
    port_vol = portfolio_volatility(weights, cov_matrix)
    marginal_risk = (cov_matrix @ weights) / port_vol
    return weights * marginal_risk