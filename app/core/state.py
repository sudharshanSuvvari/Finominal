from pandas import DataFrame


class AppState:
    returns_df: DataFrame | None = None
    factors_df: DataFrame | None = None
    securities_df: DataFrame | None = None

    DIVIDEND_YIELDS = {
        "IEFA": 0.0312,
        "GLD": 0.0,
        "AGG": 0.0345,
        "VEA": 0.0308,
        "SPY": 0.0121,
    }
    
app_state = AppState()