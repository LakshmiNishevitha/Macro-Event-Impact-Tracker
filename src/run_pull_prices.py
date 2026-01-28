from __future__ import annotations

import pandas as pd
from src.config import ASSETS
from src.events import load_events
from src.market_data import fetch_prices


def main():
    events = load_events("data/events.csv")

    start = (events["date"].min() - pd.Timedelta(days=10)).date().isoformat()
    end = (events["date"].max() + pd.Timedelta(days=30)).date().isoformat()


    tickers = list(ASSETS.values())
    prices = fetch_prices(tickers, start=start, end=end)

    prices.to_parquet("data/prices.parquet")

    print("Saved data/prices.parquet")
    print("Shape:", prices.shape)
    print("Date range:", prices.index.min().date(), "to", prices.index.max().date())
    print("Missing % per ticker:")
    print((prices.isna().mean() * 100).round(2))
    print("\nHead:")
    print(prices.head())


if __name__ == "__main__":
    main()
