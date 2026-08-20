from typing import Mapping

import pandas as pd
import streamlit as st

from src.charts import create_rate_inflation_chart, create_real_rate_chart
from src.config import CHART_CONFIG
from src.formatters import build_display_table, dataframe_to_csv, format_month


def render_header() -> None:
    st.title("U.S. Interest Rates Dashboard")
    st.write(
        "Three-month U.S. Treasury bill rate."
    )


def render_metric_cards(latest_metrics: Mapping[str, object]) -> None:

    column_1, column_2, column_3, column_4 = st.columns(4)

    column_1.metric(
        label="Latest common month",
        value=format_month(latest_metrics["date"]),
    )
    column_2.metric(
        label="Nominal rate",
        value=f"{latest_metrics['nominal_rate']:.2f}%",
    )
    column_3.metric(
        label="Expected inflation",
        value=f"{latest_metrics['expected_inflation']:.2f}%",
    )
    column_4.metric(
        label="Estimated real rate",
        value=f"{latest_metrics['real_rate']:.2f}%",
    )


def render_data_status(data_status: Mapping[str, pd.Timestamp]) -> None:
    st.subheader("Data availability")
    status_column_1, status_column_2, status_column_3 = st.columns(3)

    status_column_1.write("**TB3MS latest observation**")
    status_column_1.write(format_month(data_status["nominal_latest"]))

    status_column_2.write("**EXPINF1YR latest observation**")
    status_column_2.write(format_month(data_status["expected_latest"]))

    status_column_3.write("**Latest common observation**")
    status_column_3.write(format_month(data_status["analysis_latest"]))

    if data_status["expected_latest"] > data_status["nominal_latest"]:
        st.info(
            "Expected inflation is available through "
            f"{format_month(data_status['expected_latest'])}, "
            "but the three-month Treasury bill rate is only available through "
            f"{format_month(data_status['nominal_latest'])}. "
            "The chart therefore ends at the latest common month."
        )
    elif data_status["nominal_latest"] > data_status["expected_latest"]:
        st.info(
            "The three-month Treasury bill rate is available through "
            f"{format_month(data_status['nominal_latest'])}, "
            "but expected inflation is only available through "
            f"{format_month(data_status['expected_latest'])}."
        )
    else:
        st.success(
            "Both series are currently available through "
            f"{format_month(data_status['analysis_latest'])}."
        )


def render_charts(
    dataframe: pd.DataFrame,
    selected_chart: str,
) -> None:

    st.subheader("Interest-rate chart")

    if selected_chart == "Expected Inflation":
        figure = create_rate_inflation_chart(dataframe)

        caption = (
            "Source: FRED series TB3MS and Cleveland Fed EXPINF1YR. "
            "Monthly observations."
        )

    else:
        figure = create_real_rate_chart(dataframe)

        caption = (
            "Estimated real rate ≈ three-month Treasury bill rate "
            "− one-year expected inflation."
        )

    st.plotly_chart(
        figure,
        width="stretch",
        config={
            "displaylogo": False,
            "scrollZoom": False,
        },
    )

    st.caption(caption)

def render_data_table(dataframe: pd.DataFrame, selected_chart: str,) -> None:
    st.subheader("Monthly data")

    table = build_display_table(dataframe, selected_chart,)

    st.dataframe(table, use_container_width=True, height=420,)

    if selected_chart == "Expected Inflation":
        file_name = "us_interest_rate_expected_inflation.csv"
    else:
        file_name = "us_real_interest_rates.csv"

    st.download_button(
        label="Download data as CSV",
        data=dataframe_to_csv(
            dataframe,
            selected_chart,
        ),
        file_name=file_name, mime="text/csv", on_click="ignore",)

def render_methodology() -> None:

    with st.expander("Methodology and limitations"):
        st.markdown(
            r"""
### Fisher approximation

\[
r = i -  πᵉ
\]

Where:

- \(i\) is the nominal three-month Treasury bill rate.
- \(πᵉ\) is one-year expected inflation.
- \(r\) is the estimated ex-ante real interest rate.

### Data sources

- `TB3MS`: Federal Reserve Board, H.15 Selected Interest Rates.
- `EXPINF1YR`: Federal Reserve Bank of Cleveland.
- Both series are retrieved through FRED.

### Limitation

The nominal rate has a three-month maturity, while the expected-inflation
series has a one-year horizon. The resulting real rate should therefore be
interpreted as an approximation.
            """
        )