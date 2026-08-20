START_DATE = "2000-01-01"
CACHE_TTL_SECONDS = 6 * 60 * 60

PAGE_TITLE = "U.S. Real Interest Rate Dashboard"
PAGE_LAYOUT = "wide"

SERIES_CONFIG = {
    "nominal_rate": {
        "series_id": "TB3MS",
        "column_name": "nominal_rate",
    },
    "expected_inflation": {
        "series_id": "EXPINF1YR",
        "column_name": "expected_inflation",
    },
}

CHART_CONFIG = {
    "displaylogo": False,
    "scrollZoom": False,
}
