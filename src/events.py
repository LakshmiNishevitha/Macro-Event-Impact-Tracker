from __future__ import annotations
import pandas as pd


REQUIRED_COLS = ["event_name", "date", "country"]


def load_events(path: str = "data/events.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"events.csv missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()

    for col in ["actual", "forecast", "previous"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["event_name", "date"]).reset_index(drop=True)
    return df
