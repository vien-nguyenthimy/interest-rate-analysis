from typing import Dict

import pandas as pd
from fredapi import Fred

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

def fetch_fred_series(
    fred: Fred,
    series_id: str,
    column_name: str,
    start_date: str = "2000-01-01",
) -> pd.DataFrame:
    """
    Download one FRED series and convert it into a clean DataFrame.

    Parameters
    ----------
    fred: An authenticated FRED client.
    series_id: The FRED identifier of the requested series.
    column_name: The name assigned to the value column.
    start_date: First observation date in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        DataFrame with a DatetimeIndex named ``date`` and one value column.
    """

    try: # Python hãy thử gọi FRED. Nếu xảy ra lỗi thì thông báo rằng không thể lấy chuỗi nào
        series = fred.get_series(
            series_id,
            observation_start=start_date,
        )
    except Exception as error:
        raise RuntimeError(
            f"Could not retrieve FRED series {series_id}."
        ) from error

    # Chuyển thành DataFrame và đặt tên cột
    dataframe = (
        series
        .rename(column_name)
        .to_frame()
    )

    dataframe.index = pd.to_datetime(dataframe.index) # Lệnh này bảo đảm index thật sự có kiểu ngày tháng
    dataframe.index.name = "date" # Đặt tên cho Index

    dataframe[column_name] = pd.to_numeric( # Chuyển cột thành kiểu số, nếu không chuyển được thì đặt NaN
        dataframe[column_name],
        errors="coerce", # nếu gặp giá trị không thể chuyển thành số thì biến nó thành NaN
    )
 
    dataframe = ( # Sắp xếp theo index và loại bỏ các index trùng lặp, giữ lại giá trị cuối cùng
        dataframe
        .sort_index() # Sắp xếp
        .loc[lambda df: ~df.index.duplicated(keep="last")] # Xóa ngày trùng
    )

    return dataframe # Trả về DataFrame đã được làm sạch

def load_interest_rate_data(
    api_key: str, # FRED API key
    start_date: str = "2000-01-01", # Ngày bắt đầu lấy dữ liệu
) -> Dict[str, pd.DataFrame]:
    """
    Load the nominal interest-rate and expected-inflation series.

    Parameters
    ----------
    api_key: FRED API key.
    start_date: First observation date in YYYY-MM-DD format.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing separate nominal-rate and
        expected-inflation DataFrames.
    """

    if not api_key or not api_key.strip(): # Nếu không có API key hợp lệ thì báo lỗi
        raise ValueError("A valid FRED API key is required.")

    fred = Fred(api_key=api_key) # Tạo một đối tượng FRED với API key

    nominal_config = SERIES_CONFIG["nominal_rate"] # Lấy cấu hình cho chuỗi lãi suất danh nghĩa
    expected_config = SERIES_CONFIG["expected_inflation"] # Lấy cấu hình cho chuỗi lạm phát kỳ vọng

    nominal_df = fetch_fred_series( # Gọi hàm fetch_fred_series để lấy dữ liệu lãi suất danh nghĩa
        fred=fred,
        series_id=nominal_config["series_id"],
        column_name=nominal_config["column_name"],
        start_date=start_date,
    )

    expected_df = fetch_fred_series( # Gọi hàm fetch_fred_series để lấy dữ liệu lạm phát kỳ vọng
        fred=fred,
        series_id=expected_config["series_id"],
        column_name=expected_config["column_name"],
        start_date=start_date,
    )

    return {
        "nominal_rate": nominal_df,
        "expected_inflation": expected_df,
    }