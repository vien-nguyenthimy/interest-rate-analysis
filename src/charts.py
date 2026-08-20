from turtle import st

import pandas as pd
import plotly.graph_objects as go


def _validate_chart_data(dataframe: pd.DataFrame, columns: set[str]) -> None:
    missing_columns = columns.difference(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Chart data is missing required columns: {missing}.")

    if dataframe.empty:
        raise ValueError("Chart data cannot be empty.")


def create_rate_inflation_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Compare the Treasury bill rate with expected inflation."""

    _validate_chart_data(
        dataframe,
        {"nominal_rate", "expected_inflation"},
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=dataframe.index,
            y=dataframe["nominal_rate"],
            name="Interest Rate",
            mode="lines",
            line={"color": "#252525", "width": 2.2},
            hovertemplate=(
                "%{x|%B %Y}<br>"
                "Interest rate: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=dataframe.index,
            y=dataframe["expected_inflation"],
            name="Expected Inflation",
            mode="lines",
            line={"color": "#0099E5", "width": 2.2},
            hovertemplate=(
                "%{x|%B %Y}<br>"
                "Expected inflation: %{y:.2f}%"
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
                "Expected Inflation and Interest Rates "
                "(Three-Month Treasury Bills), "
                f"{dataframe.index.min().year}–"
                f"{dataframe.index.max().year}"
            ),
            "x": 0.01,
        },
        xaxis_title="Year",
        yaxis_title="Annual Rate (%)",
        hovermode="x unified",
        height=560,
        template="plotly_white",
        font={"color": "#252525"},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        margin={"l": 30, "r": 30, "t": 90, "b": 40},
    )
    return figure


def create_real_rate_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Compare the nominal rate with the estimated real rate."""

    _validate_chart_data(
        dataframe,
        {"nominal_rate", "real_rate_approx"},
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=dataframe.index,
            y=dataframe["nominal_rate"],
            name="Nominal Rate",
            mode="lines",
            line={"color": "#262626", "width": 2.2},
            hovertemplate=(
                "%{x|%B %Y}<br>"
                "Nominal rate: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            x=dataframe.index,
            y=dataframe["real_rate_approx"],
            name="Estimated Real Rate",
            mode="lines",
            line={"color": "#1495D1", "width": 2.2},
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
                f"{dataframe.index.min().year}–"
                f"{dataframe.index.max().year}"
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
        margin={"l": 30, "r": 30, "t": 90, "b": 40},
    )

    return figure
