# Interest Rate Analysis

A Streamlit dashboard for exploring U.S. interest rates and estimating the
ex-ante real interest rate from January 2000 to the latest available monthly
observation.

The project retrieves data from FRED, applies the Fisher equation, and presents
the results through interactive Plotly charts, summary metrics, monthly tables,
and downloadable CSV files.

## Project objective

The project aims to answer the following questions:

- How has the U.S. nominal interest rate changed since 2000?
- What is the estimated real interest rate after accounting for expected inflation?
- During which periods was the estimated real interest rate negative?
- How different are the approximate and exact Fisher equations?
- How can the dashboard automatically incorporate newly released monthly data?

## Dashboard views

The sidebar allows users to switch between two views.

### Real Interest Rate

This view compares:

- the nominal three-month Treasury bill rate; and
- the estimated ex-ante real interest rate.

Its monthly table includes the nominal rate, expected inflation, approximate
real rate, exact real rate, and a negative-real-rate indicator. The Fisher
methodology and its limitations are displayed only in this view.

### Expected Inflation

This view compares:

- the three-month Treasury bill rate; and
- one-year expected inflation.

Its monthly table contains only the fields relevant to the chart: month,
nominal interest rate, and expected inflation.

## Main features

- Retrieve the latest monthly observations from FRED
- Switch between two charts from the sidebar
- Select a custom chart start date
- Display the latest common observation and summary metrics
- Identify differences in data availability between the two FRED series
- Calculate approximate and exact real interest rates
- Identify months with a negative estimated real interest rate
- Display a table relevant to the selected chart
- Download only the data relevant to the selected chart
- Refresh FRED data manually
- Cache API responses for six hours

## Methodology

According to the Fisher equation:

$$
1+i=(1+r)(1+πᵉ)
$$

where:

- \(i\): nominal interest rate
- \(r\): ex-ante real interest rate
- \(πᵉ\): expected inflation rate

### Approximate Fisher equation

The main estimated real interest rate is calculated as:

$$
r \approx i-\pi^e
$$

In Python:

```python
real_rate_approx = nominal_rate - expected_inflation
```

### Exact Fisher equation

The exact real interest rate is calculated as:

$$
r=\frac{1+i}{1+πᵉ}-1
$$

Because the original data are expressed in percentages, the Python calculation is:

```python
real_rate_exact = (
    (1 + nominal_rate / 100)
    / (1 + expected_inflation / 100)
    - 1
) * 100
```

## Why expected inflation instead of CPI?

This project estimates the **ex-ante real interest rate**. It measures the real interest rate expected by investors at the time an investment decision is made.

Expected inflation is therefore used instead of realized CPI inflation:

$$
r_t^{ex\text{-}ante}
\approx
i_t-E_t(\pi_{t+1})
$$

CPI describes inflation that has already occurred, while expected inflation represents beliefs about future inflation.

A CPI-based real rate could be added as a separate **ex-post real rate proxy**, but it answers a different economic question.

## Data sources

| Variable | FRED series | Description |
|---|---|---|
| Nominal interest rate | `TB3MS` | 3-Month Treasury Bill Secondary Market Rate |
| Expected inflation | `EXPINF1YR` | Cleveland Fed 1-Year Expected Inflation |

Sources:

- [3-Month Treasury Bill Rate – FRED](https://fred.stlouisfed.org/series/TB3MS)
- [1-Year Expected Inflation – FRED](https://fred.stlouisfed.org/series/EXPINF1YR)

Both series are retrieved automatically through the FRED API.

## Important limitation

`TB3MS` has a three-month maturity, while `EXPINF1YR` represents expected
inflation over a one-year horizon. The estimated real rate should therefore be
interpreted as an approximation rather than a perfectly maturity-matched real
interest rate.

## Project structure

```text
interest-rate-analysis/
│
├── app.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── calculations.py
│   ├── charts.py
│   ├── formatters.py
│   ├── dashboard_components.py
│
├── data/
│   ├── raw/
│   │   ├── tb3ms_monthly.csv
│   │   └── expected_inflation.csv
│   └── processed/
│       └── real_interest_rate_ex_ante.csv
│
├── notebooks/
│   └── fed_real_interest_rate.ipynb
│
├── outputs/
    └── *.png
```

### Main modules

| File | Responsibility |
|---|---|
| `app.py` | Coordinates data loading, sidebar controls, filtering, and dashboard rendering |
| `src/config.py` | Stores shared settings and FRED series configuration |
| `src/data_loader.py` | Retrieves and cleans FRED data |
| `src/calculations.py` | Joins the series and calculates real interest rates |
| `src/charts.py` | Builds reusable Plotly figures |
| `src/formatters.py` | Prepares chart-specific tables and CSV files |
| `src/dashboard_components.py` | Renders Streamlit dashboard sections |

The main application flow is:

```text
app.py
  → data_loader.py
  → calculations.py
  → dashboard_components.py
      → charts.py
      → formatters.py
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/vien-nguyenthimy/us-real-interest-rate-analysis.git
cd interest-rate-analysis
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the required libraries

```bash
pip install -r requirements.txt
```

### 4. Configure the FRED API key

Create a local `.env` file in the project root:

```env
FRED_API_KEY=your_fred_api_key
```

The `.env` file is excluded from Git through `.gitignore` and must never be committed to GitHub.

You can request an API key from the
[FRED website](https://fredaccount.stlouisfed.org/apikeys).

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

## Streamlit Cloud deployment

When deploying on Streamlit Community Cloud, add the API key under:

```text
App settings → Secrets
```

Use the following format:

```toml
FRED_API_KEY = "your_fred_api_key"
```

Do not upload the `.env` file to GitHub.


## Author

**Nguyen Thi My Vien**
