# Macro Event Impact Tracker (Daily)

A reproducible **event-study analysis tool** that measures how major U.S. macroeconomic events
(CPI, NFP, PMI, FOMC) impact a cross-asset market basket using **daily price data**.

The project focuses on **correct event alignment**, **clean return computation**, and
**interpretable macro insights**, rather than complex modeling.

---

## What this project does

For each macro event, the system:

- stores event metadata (event type, date, optional actual / forecast / previous)
- maps events to the correct **trading day**
- pulls daily prices for a predefined asset basket
- computes:
  - same-day return  
  - next-day return  
  - two-day cumulative return
- classifies an approximate **yield-curve regime** using bond ETF proxies
- generates:
  - an interactive **Streamlit dashboard**
  - a one-page **HTML event report** with charts, tables, and narrative summary

---

## Asset basket (daily ETF proxies)

| Asset class | Ticker | Purpose |
|------------|--------|--------|
| US equities | SPY | Risk-on response |
| USD | UUP | Dollar strength proxy |
| Short Treasuries | SHY | Short-end rates |
| Mid Treasuries | IEF | Curve context |
| Long Treasuries | TLT | Long-end rates |
| Gold | GLD | Inflation / hedge |
| Oil | USO | Energy / inflation impulse |

ETFs are used to avoid data quality issues common with raw FX or yield tickers at daily frequency.

---

## Yield curve classification (daily proxy)

Bond ETF price moves are used as a **directional proxy** for yield changes:

- Bond price ↓ ⇒ yield ↑  
- Bond price ↑ ⇒ yield ↓  

Using same-day returns of SHY and TLT, events are labeled as:

- `bear_steepening`
- `bear_flattening`
- `bull_steepening`
- `bull_flattening`
- `twist`

This classification is **approximate by design** and intended for interpretability, not precision trading.

---

## Project structure

```text
macro-impact-tracker/
├── app/ # Streamlit dashboard
├── data/
│ ├── events.csv # Event calendar
│ ├── prices.parquet # Daily prices
│ └── event_impacts.parquet
├── reports/ # Exported HTML reports
├── src/ # Data pipeline & analytics
├── assets/ # Screenshots (optional)
├── requirements.txt
└── README.md
```
---

## How to run the project

### 1) Environment setup
Create and activate a virtual environment, then install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Add or edit macro events
Edit the file:
```bash
data/events.csv
```
Required columns:
event_name (CPI, NFP, PMI, FOMC)
date (YYYY-MM-DD)
country
Optional columns:
actual
forecast
previous

### 3) Pull daily market data
Fetch daily prices for the asset basket and save them locally.
```bash
python -m src.run_pull_prices
```
This generates:
```bash
data/prices.parquet
```

### 4) Compute event impacts
Calculate same-day, next-day, and two-day cumulative returns for each event.
```bash
python -m src.run_compute_impacts
python -m src.run_add_curve_labels
```
This generates:
```bash
data/event_impacts.parquet
```
### 5) Launch the Streamlit dashboard
Run the interactive dashboard to explore event reactions.
```bash
streamlit run app/app.py
```
Use the sidebar to select:
event type
event trading date

### 6) Export HTML event reports
Generate one-page HTML reports for each event.
```bash
python -m src.run_export_reports
```
Reports are saved in:
```bash
reports/
```
Each report is named:
```bash
US_<EVENT>_<YYYY-MM-DD>.html
```

---
