# src/run_add_curve_labels.py
from __future__ import annotations
import pandas as pd
from src.curve import classify_curve_move


def main():
    df = pd.read_parquet("data/event_impacts.parquet")

    labels = []
    for (event_name, event_date), g in df.groupby(["event_name", "event_date_trading"]):
        shy = g.loc[g["ticker"] == "SHY", "same_day_return"]
        tlt = g.loc[g["ticker"] == "TLT", "same_day_return"]

        if shy.empty or tlt.empty:
            label = "unknown"
        else:
            label = classify_curve_move(float(shy.iloc[0]), float(tlt.iloc[0]))

        labels.append({"event_name": event_name, "event_date_trading": event_date, "curve_label": label})

    labels_df = pd.DataFrame(labels)
    df = df.merge(labels_df, on=["event_name", "event_date_trading"], how="left")

    df.to_parquet("data/event_impacts.parquet", index=False)

    print("Updated data/event_impacts.parquet with curve_label")
    print(df[["event_name", "event_date_trading", "curve_label"]].drop_duplicates().head(20))


if __name__ == "__main__":
    main()
