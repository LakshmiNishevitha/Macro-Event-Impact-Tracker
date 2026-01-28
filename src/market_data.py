from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """
    Fetch daily prices from Yahoo Finance.
    Uses Adj Close when available; falls back to Close.
    Returns: DataFrame indexed by trading date, columns=tickers.
    """
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if isinstance(data.columns, pd.MultiIndex):
        if "Adj Close" in data.columns.get_level_values(0):
            px = data["Adj Close"].copy()
        else:
            px = data["Close"].copy()
    else:
        col = "Adj Close" if "Adj Close" in data.columns else "Close"
        px = data[[col]].copy()
        px.columns = tickers

    px.index = pd.to_datetime(px.index).normalize()

    px = px.dropna(how="all")

    return px
