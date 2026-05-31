from pathlib import Path

import pandas as pd


def read_excel_sheet(
    file_path: str | Path,
    sheet_name: str,
) -> pd.DataFrame:
    """
    Read a sheet from an Excel workbook.
    """

    return pd.read_excel(
        file_path,
        sheet_name=sheet_name,
    )

def load_portfolio_data(
    file_path: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    returns_df = read_excel_sheet(
        file_path=file_path,
        sheet_name="Fund Returns",
    )

    factors_df = read_excel_sheet(
        file_path=file_path,
        sheet_name="Factor Returns",
    )

    securities_df = read_excel_sheet(
        file_path=file_path,
        sheet_name="Fund Info",
    )
    
    return (
        returns_df,
        factors_df,
        securities_df,
    )