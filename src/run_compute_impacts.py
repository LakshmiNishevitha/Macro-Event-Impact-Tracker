# src/run_compute_impacts.py
from __future__ import annotations

import pandas as pd
from src.events import load_events
from src.impact import compute_event_impacts


def main():
    events = load_events("data/events.csv")
    prices = pd.read_parquet("data/prices.parquet")

    last_price_date = prices.index.max()
    events = events[events["date"] <= last_price_date].copy()

    impacts = compute_event_impacts(events, prices, z_window=60)
    impacts.to_parquet("data/event_impacts.parquet")

    print("Last price date:", last_price_date.date().isoformat())
    print("Events kept:", len(events))
    print("Saved data/event_impacts.parquet")
    print("Rows:", len(impacts))
    print("\nSample:")
    print(impacts.head(10))


if __name__ == "__main__":
    main()
