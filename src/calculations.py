from typing import Dict

import pandas as pd

def build_analysis_dataset(
    nominal_df: pd.DataFrame,
    expected_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine nominal-rate and expected-inflation data and calculate
    approximate and exact ex-ante real interest rates.

    Parameters
    ----------
    nominal_df:
        DataFrame containing a ``nominal_rate`` column.
    expected_df:
        DataFrame containing an ``expected_inflation`` column.

    Returns
    -------
    pd.DataFrame
        Monthly analysis dataset containing nominal, expected-inflation,
        and estimated real-interest-rate variables.
    """

    if "nominal_rate" not in nominal_df.columns:
        raise ValueError(
            "nominal_df must contain a 'nominal_rate' column."
        )

    if "expected_inflation" not in expected_df.columns:
        raise ValueError(
            "expected_df must contain an "
            "'expected_inflation' column."
        )

    analysis_df = nominal_df[["nominal_rate"]].join(
        expected_df[["expected_inflation"]],
        how="inner",
    )

    analysis_df = analysis_df.dropna().sort_index()

    if analysis_df.empty:
        raise ValueError(
            "No overlapping observations were found."
        )

     # Fisher approximation: r ≈ i - πᵉ
    analysis_df["real_rate_approx"] = (
        analysis_df["nominal_rate"]
        - analysis_df["expected_inflation"]
    )

    # Exact Fisher equation:
    # r = ((1 + i) / (1 + πᵉ)) - 1
    nominal_decimal = ( 
        analysis_df["nominal_rate"] / 100
    )

    expected_decimal = (
        analysis_df["expected_inflation"] / 100
    )

    analysis_df["real_rate_exact"] = (
        (
            (1 + nominal_decimal)
            / (1 + expected_decimal)
        ) - 1
    ) * 100

    analysis_df["formula_difference"] = (
        analysis_df["real_rate_approx"]
        - analysis_df["real_rate_exact"]
    )

    analysis_df["negative_real_rate"] = (
        analysis_df["real_rate_approx"] < 0
    )

    return analysis_df

def get_data_status(
    nominal_df: pd.DataFrame,
    expected_df: pd.DataFrame,
    analysis_df: pd.DataFrame,
) -> Dict[str, pd.Timestamp]:
    """
    Return the latest available date for each source and the latest
    common date used in the analysis.
    """

    nominal_valid = nominal_df["nominal_rate"].dropna()
    expected_valid = expected_df["expected_inflation"].dropna()

    nominal_latest = (
        nominal_valid.index.max()
        if not nominal_valid.empty
        else pd.NaT
    )

    expected_latest = (
        expected_valid.index.max()
        if not expected_valid.empty
        else pd.NaT
    )

    analysis_latest = (
        analysis_df.index.max()
        if not analysis_df.empty
        else pd.NaT
    )

    return {
        "nominal_latest": nominal_latest,
        "expected_latest": expected_latest,
        "analysis_latest": analysis_latest,
    }

def get_latest_metrics(
    analysis_df: pd.DataFrame,
) -> Dict[str, object]:
    """
    Return the most recent common observation and its key indicators.
    """

    if analysis_df.empty:
        raise ValueError(
            "The analysis DataFrame is empty."
        )

    latest_date = analysis_df.index.max()
    latest_row = analysis_df.loc[latest_date]

    return {
        "date": latest_date,
        "nominal_rate": float(
            latest_row["nominal_rate"]
        ),
        "expected_inflation": float(
            latest_row["expected_inflation"]
        ),
        "real_rate": float(
            latest_row["real_rate_approx"]
        ),
        "is_negative": bool(
            latest_row["negative_real_rate"]
        ),
    }