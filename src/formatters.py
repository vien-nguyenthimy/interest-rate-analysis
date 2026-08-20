
import pandas as pd


REAL_RATE_TABLE_COLUMNS = {
    "nominal_rate": "Nominal Rate (%)",
    "expected_inflation": "Expected Inflation (%)",
    "real_rate_approx": "Real Rate – Approx. (%)",
    "real_rate_exact": "Real Rate – Exact (%)",
    "negative_real_rate": "Negative Real Rate",
}

EXPECTED_INFLATION_TABLE_COLUMNS = {
    "nominal_rate": "Nominal Rate (%)",
    "expected_inflation": "Expected Inflation (%)",
}


def format_month(date: pd.Timestamp) -> str:
    if pd.isna(date):
        return "Unavailable"
    
    return date.strftime("%B %Y")

def get_table_columns(selected_chart: str) -> dict[str, str]:
    if selected_chart == "Expected Inflation":
        return EXPECTED_INFLATION_TABLE_COLUMNS

    return REAL_RATE_TABLE_COLUMNS

def build_display_table(dataframe: pd.DataFrame, 
                        selected_chart: str = "Real Interest Rate"
                        ) -> pd.DataFrame:

    table_columns = get_table_columns(selected_chart)

    table = dataframe[list(table_columns)].copy()
    table = table.rename(columns=table_columns)

    table.index = table.index.strftime("%Y-%m")
    table.index.name = "Month"

    return table.sort_index(ascending=False)


def dataframe_to_csv(dataframe: pd.DataFrame, selected_chart: str = "Real Interest Rate") -> bytes:

    table_columns = get_table_columns(selected_chart)
    download_data = dataframe[list(table_columns)].reset_index()
    return download_data.to_csv(index=False).encode("utf-8")
