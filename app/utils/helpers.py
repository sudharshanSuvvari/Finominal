def build_allocation_changes(
    holdings,
    selected_returns,
    optimized_weights,
    securities_df,
):
    result = []
    weights_by_ticker = dict(
    zip(
        selected_returns.columns,
        optimized_weights,
    )
)

    for holding in holdings:

        optimized_weight = (
            weights_by_ticker[
                holding.ticker
            ]
        )

        ticker = holding.ticker
        current_weight = holding.weight

        security_name = (
            securities_df.loc[
                securities_df["ticker"] == ticker,
                "fund_name",
            ]
            .iloc[0]
        )

        result.append(
            {
                "ticker": ticker,
                "security_name": security_name,
                "current_weight": round(
                    current_weight,
                    2,
                ),
                "optimized_weight": round(
                    optimized_weight * 100,
                    2,
                ),
                "change": round(
                    optimized_weight * 100
                    - current_weight,
                    2,
                ),
            }
        )

    return result