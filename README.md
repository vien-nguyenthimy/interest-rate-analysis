# Interest Rate Analysis

A Streamlit dashboard for analyzing the U.S. nominal interest rate and estimating the ex-ante real interest rate from 2000 to the latest available monthly observation.

The project is inspired by the real and nominal interest rate chart presented in *The Economics of Money, Banking, and Financial Markets* by Frederic S. Mishkin.

## Project objective

The project aims to answer the following questions:

- How has the U.S. nominal interest rate changed since 2000?
- What is the estimated real interest rate after accounting for expected inflation?
- During which periods was the estimated real interest rate negative?
- How different are the approximate and exact Fisher equations?
- How can the dashboard automatically incorporate newly released monthly data?

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

## Dashboard features

- Retrieve the latest monthly data from FRED
- Select a custom analysis period
- Display nominal and estimated real interest rates
- Show a zero-interest reference line
- Identify periods with negative real interest rates
- Compare approximate and exact Fisher calculations
- Display the latest available observations
- Download the processed dataset as a CSV file
- Refresh data when new observations become available

## Project structure

```text
us-real-interest-rate-analysis/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── calculations.py
│
├── data/
├── notebooks/
└── outputs/
```

Main files:

- `app.py`: Streamlit dashboard interface
- `src/data_loader.py`: retrieves and cleans FRED data
- `src/calculations.py`: joins the series and calculates real interest rates

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/vien-nguyenthimy/us-real-interest-rate-analysis.git
cd us-real-interest-rate-analysis
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
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

You can request a FRED API key from:

https://fredaccount.stlouisfed.org/apikeys

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
