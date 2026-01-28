# src/run_export_reports.py
from __future__ import annotations

import pandas as pd
from src.report import generate_event_report


def main():
    impacts = pd.read_parquet("data/event_impacts.parquet")
    events = pd.read_csv("data/events.csv", parse_dates=["date"])
    events["date"] = events["date"].dt.normalize()

    # Export ALL unique event_name + trading_date pairs
    pairs = impacts[["event_name", "event_date_trading"]].drop_duplicates().sort_values(["event_name", "event_date_trading"])

    paths = []
    for _, r in pairs.iterrows():
        p = generate_event_report(
            impacts=impacts,
            events_csv=events,
            event_name=r["event_name"],
            trading_date=r["event_date_trading"],
            out_dir="reports",
        )
        paths.append(str(p))

    print("Generated reports:")
    for p in paths:
        print(" -", p)


if __name__ == "__main__":
    main()
