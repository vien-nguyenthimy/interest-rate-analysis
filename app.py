import os
from datetime import datetime, timezone

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dotenv import load_dotenv

from src.data_loader import load_interest_rate_data
from src.calculations import (
    build_analysis_dataset,
    get_data_status,
    get_latest_metrics,
)


START_DATE = "2000-01-01"
CACHE_TTL_SECONDS = 6 * 60 * 60


st.set_page_config(page_title="U.S. Real Interest Rate Dashboard",layout="wide",)


def get_fred_api_key() -> str:
    """Read the FRED API key locally or from Streamlit secrets."""

    load_dotenv()

    api_key = os.getenv("FRED_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["FRED_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        st.error(
            "FRED API key was not found. "
            "Add FRED_API_KEY to your .env file."
        )
        st.stop()

    return api_key


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False,)
def load_dashboard_data(_api_key: str, start_date: str,):
    """
    Load FRED data and calculate the estimated real interest rate.

    The leading underscore in _api_key tells Streamlit not to include
    the API key when creating the cache key.
    """

    raw_data = load_interest_rate_data(
        api_key=_api_key,
        start_date=start_date,
    )

    nominal_df = raw_data["nominal_rate"]
    expected_df = raw_data["expected_inflation"]

    analysis_df = build_analysis_dataset(
        nominal_df=nominal_df,
        expected_df=expected_df,
    )

    fetched_at = datetime.now(timezone.utc)

    return (nominal_df, expected_df, analysis_df, fetched_at,)


def format_month(date: pd.Timestamp) -> str:
    """Convert a timestamp into a readable month and year."""

    if pd.isna(date):
        return "Unavailable"

    return date.strftime("%B %Y")


fred_api_key = get_fred_api_key()


# Sidebar
st.sidebar.title("Dashboard controls")

if st.sidebar.button("Refresh FRED data"):
    load_dashboard_data.clear()
    st.rerun()


# Load data
try:
    with st.spinner("Loading the latest FRED data..."):
        (
            nominal_df,
            expected_df,
            analysis_df,
            fetched_at,
        ) = load_dashboard_data(
            _api_key=fred_api_key,
            start_date=START_DATE,
        )

except Exception as error:
    st.error(
        "The dashboard could not load FRED data."
    )

    st.code(str(error))
    st.stop()


# Date filter
selected_start_date = st.sidebar.date_input(
    "Chart start date",
    value=analysis_df.index.min().date(),
    min_value=analysis_df.index.min().date(),
    max_value=analysis_df.index.max().date(),
)

filtered_df = analysis_df.loc[analysis_df.index >= pd.Timestamp(selected_start_date)].copy()


# Dashboard title
st.title("U.S. Nominal and Estimated Real Interest Rates")

st.write(
    "Three-month U.S. Treasury bill rate and estimated "
    "ex-ante real interest rate."
)


# Latest data
data_status = get_data_status(
    nominal_df=nominal_df,
    expected_df=expected_df,
    analysis_df=analysis_df,
)

latest_metrics = get_latest_metrics(analysis_df=analysis_df)


# Metric cards
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


# Data availability status
st.subheader("Data availability")

status_column_1, status_column_2, status_column_3 = (
    st.columns(3)
)

status_column_1.write(
    "**TB3MS latest observation**"
)

status_column_1.write(
    format_month(
        data_status["nominal_latest"]
    )
)

status_column_2.write(
    "**EXPINF1YR latest observation**"
)

status_column_2.write(
    format_month(
        data_status["expected_latest"]
    )
)

status_column_3.write(
    "**Latest common observation**"
)

status_column_3.write(format_month(data_status["analysis_latest"]))


# Explain mismatched latest months
if (
    data_status["expected_latest"]
    > data_status["nominal_latest"]
):
    st.info(
        "Expected inflation is available through "
        f"{format_month(data_status['expected_latest'])}, "
        "but the three-month Treasury bill rate is only "
        "available through "
        f"{format_month(data_status['nominal_latest'])}. "
        "The chart therefore ends at the latest common month."
    )

elif (
    data_status["nominal_latest"]
    > data_status["expected_latest"]
):
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


# Interactive chart
st.subheader("Interest-rate chart")

figure = go.Figure()

figure.add_trace(
    go.Scatter(
        x=filtered_df.index,
        y=filtered_df["nominal_rate"],
        name="Nominal Rate",
        mode="lines",
        line={
            "color": "#262626",
            "width": 2.2,
        },
        hovertemplate=(
            "%{x|%B %Y}<br>"
            "Nominal rate: %{y:.2f}%"
            "<extra></extra>"
        ),
    )
)

figure.add_trace(
    go.Scatter(
        x=filtered_df.index,
        y=filtered_df["real_rate_approx"],
        name="Estimated Real Rate",
        mode="lines",
        line={
            "color": "#1495D1",
            "width": 2.2,
        },
        hovertemplate=(
            "%{x|%B %Y}<br>"
            "Estimated real rate: %{y:.2f}%"
            "<extra></extra>"
        ),
    )
)

figure.add_hline(
    y=0,
    line_dash="dash",
    line_color="#777777",
    line_width=1,
)

figure.update_layout(
    title={
        "text": (
            "U.S. Nominal and Estimated Real Interest Rates, "
            f"{filtered_df.index.min().year}–"
            f"{filtered_df.index.max().year}"
        ),
        "x": 0.01,
    },
    xaxis_title="Year",
    yaxis_title="Interest Rate (%)",
    hovermode="x unified",
    template="plotly_white",
    height=560,
    legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
    },
    margin={
        "l": 30,
        "r": 30,
        "t": 90,
        "b": 40,
    },
)

st.plotly_chart(
    figure,
    width="stretch",
    config={
        "displaylogo": False,
        "scrollZoom": False,
    },
)

st.caption(
    "Estimated real rate ≈ three-month Treasury bill rate "
    "− one-year expected inflation."
)


# Data table
st.subheader("Monthly data")

table_df = filtered_df[
    [
        "nominal_rate",
        "expected_inflation",
        "real_rate_approx",
        "real_rate_exact",
        "negative_real_rate",
    ]
].copy()

table_df = table_df.rename(
    columns={
        "nominal_rate": "Nominal Rate (%)",
        "expected_inflation": "Expected Inflation (%)",
        "real_rate_approx": "Real Rate – Approx. (%)",
        "real_rate_exact": "Real Rate – Exact (%)",
        "negative_real_rate": "Negative Real Rate",
    }
)

table_df.index = table_df.index.strftime(
    "%Y-%m"
)

table_df.index.name = "Month"

st.dataframe(
    table_df.sort_index(ascending=False).style.format(
        {
            "Nominal Rate (%)": "{:.2f}",
            "Expected Inflation (%)": "{:.2f}",
            "Real Rate – Approx. (%)": "{:.2f}",
            "Real Rate – Exact (%)": "{:.2f}",
        }
    ),
    width="stretch",
    height=420,
)


# CSV download
download_df = filtered_df.reset_index()

csv_data = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download data as CSV",
    data=csv_data,
    file_name="us_real_interest_rates.csv",
    mime="text/csv",
    on_click="ignore",
)


# Methodology
with st.expander("Methodology and limitations"):
    st.markdown(
        """
### Fisher approximation

\[
r = i -  πᵉ
\]

Where:

- \(i\) is the nominal three-month Treasury bill rate.
- \( πᵉ\) is one-year expected inflation.
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


st.caption(
    "FRED data fetched at "
    f"{fetched_at.strftime('%Y-%m-%d %H:%M')} UTC. "
    "The application caches API results for six hours."
)