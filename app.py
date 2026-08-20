import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.calculations import (
    build_analysis_dataset,
    get_data_status,
    get_latest_metrics,
)
from src.config import CACHE_TTL_SECONDS, PAGE_LAYOUT, PAGE_TITLE, START_DATE
from src.dashboard_components import (
    render_charts,
    render_data_status,
    render_data_table,
    render_header,
    render_methodology,
    render_metric_cards,
)
from src.data_loader import load_interest_rate_data

st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT,
)

st.set_page_config(page_title="Interest Rate Dashboard",layout="wide",)


def get_fred_api_key() -> str:
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

def load_data_or_stop(
    api_key: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, datetime]:
    """Load dashboard data and display a readable error if it fails."""

    try:
        with st.spinner("Loading the latest FRED data..."):
            return load_dashboard_data(
                _api_key=api_key,
                start_date=START_DATE,
            )
    except Exception as error:
        st.error("The dashboard could not load FRED data.")
        st.code(str(error))
        st.stop()

def select_start_date(analysis_df: pd.DataFrame) -> pd.Timestamp:
    """Render the sidebar date filter and return its selected value."""

    selected_date = st.sidebar.date_input(
        "Chart start date",
        value=analysis_df.index.min().date(),
        min_value=analysis_df.index.min().date(),
        max_value=analysis_df.index.max().date(),
    )

    return pd.Timestamp(selected_date)


def main() -> None:
    """Coordinate data loading, filtering, calculations, and UI rendering."""

    api_key = get_fred_api_key()

    st.sidebar.title("Dashboard controls")
    selected_chart = st.sidebar.radio(
    "Select chart",
    options=(
        "Real Interest Rate",
        "Expected Inflation",
        ),
    )   
    if st.sidebar.button("Refresh FRED data"):
        load_dashboard_data.clear()
        st.rerun()

    nominal_df, expected_df, analysis_df, fetched_at = load_data_or_stop(api_key)

    selected_start_date = select_start_date(analysis_df)
    filtered_df = analysis_df.loc[
        analysis_df.index >= selected_start_date
    ].copy()

    data_status = get_data_status(
        nominal_df=nominal_df,
        expected_df=expected_df,
        analysis_df=analysis_df,
    )
    latest_metrics = get_latest_metrics(analysis_df=analysis_df)

    render_header()
    render_metric_cards(latest_metrics)
    render_data_status(data_status)
    render_charts(filtered_df, selected_chart)
    render_data_table(filtered_df, selected_chart)

    if selected_chart == "Real Interest Rate":
        render_methodology()

    st.caption(
        "FRED data fetched at "
        f"{fetched_at.strftime('%Y-%m-%d %H:%M')} UTC. "
        "The application caches API results for six hours."
    )


if __name__ == "__main__":
    main()