import pandas as pd
import numpy as np


def build_allocation_changes(
    holdings,
    selected_returns,
    optimized_weights: np.ndarray,
    securities_df: pd.DataFrame,
) -> list[dict]:
    """
    Pairs current holdings with optimised weights and returns a list of dicts
    describing how each position should change.
    """
    weights_by_ticker = dict(
        zip(selected_returns.columns, optimized_weights)
    )

    result = []
    for holding in holdings:
        ticker = holding.ticker
        current_weight = holding.weight
        optimized_weight = weights_by_ticker[ticker]

        name_series = securities_df.loc[
            securities_df["ticker"] == ticker, "fund_name"
        ]
        if name_series.empty:
            raise ValueError(f"Ticker '{ticker}' not found in securities_df")
        security_name = name_series.iloc[0]

        result.append(
            {
                "ticker": ticker,
                "security_name": security_name,
                "current_weight": round(current_weight, 2),
                "optimized_weight": round(optimized_weight * 100, 2),
                "change": round(optimized_weight * 100 - current_weight, 2),
            }
        )

    return result