# app/app.py
from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache_data
def load_data():
    impacts = pd.read_parquet("data/event_impacts.parquet")
    events = pd.read_csv("data/events.csv", parse_dates=["date"])
    events["date"] = events["date"].dt.normalize()
    return impacts, events


def format_pct(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{x*100:.2f}%"


def make_summary(event_name: str, event_date: str, curve_label: str, wide: pd.DataFrame) -> str:
    """
    Simple, rule-based summary paragraph from same-day + next-day returns.
    """
    # Focus on key assets (if present)
    key_map = {
        "SPY": "equities (SPY)",
        "UUP": "USD (UUP)",
        "TLT": "long bonds (TLT)",
        "GLD": "gold (GLD)",
        "USO": "oil (USO)",
    }

    lines = [f"**{event_name}** on **{event_date}** shows a **{curve_label.replace('_',' ')}** curve proxy reaction."]

    for ticker, label in key_map.items():
        if ticker in wide.index:
            sd = wide.at[ticker, "same_day_return"]
            nd = wide.at[ticker, "next_day_return"]
            direction_sd = "up" if sd > 0 else "down" if sd < 0 else "flat"
            direction_nd = "up" if nd > 0 else "down" if nd < 0 else "flat"
            lines.append(f"- {label}: same-day **{direction_sd}** ({format_pct(sd)}), next-day **{direction_nd}** ({format_pct(nd)})")

    return "\n".join(lines)


def main():
    st.set_page_config(page_title="Macro Event Impact Tracker", layout="wide")
    st.title("Macro Event Impact Tracker (Daily)")
    st.caption("Pick an event + date to view same-day and next-day reactions across assets.")

    impacts, events = load_data()

    # Basic guards
    required_cols = {
        "event_name", "event_date_trading", "ticker",
        "same_day_return", "next_day_return", "two_day_return",
        "curve_label",
    }
    missing = required_cols - set(impacts.columns)
    if missing:
        st.error(f"event_impacts.parquet is missing columns: {sorted(missing)}")
        st.stop()

    # Sidebar controls
    with st.sidebar:
        st.header("Filters")
        event_types = sorted(impacts["event_name"].unique().tolist())
        event_name = st.selectbox("Event type", event_types)

        # dates available for this event type
        dates = (
            impacts.loc[impacts["event_name"] == event_name, "event_date_trading"]
            .dropna()
            .unique()
            .tolist()
        )
        dates = sorted(dates)
        event_date = st.selectbox("Event trading date", dates)

        show_two_day = st.checkbox("Show 2-day cumulative return", value=True)
        show_table = st.checkbox("Show data table", value=True)

    # Filter
    df = impacts[(impacts["event_name"] == event_name) & (impacts["event_date_trading"] == event_date)].copy()
    if df.empty:
        st.warning("No data for this selection.")
        st.stop()

    # Get curve label (should be same across rows)
    curve_label = df["curve_label"].dropna().iloc[0] if df["curve_label"].notna().any() else "unknown"

    # Event details from events.csv (optional: may be placeholders)
    raw_dates = sorted(df["event_date_raw"].unique().tolist())
    raw_date_for_lookup = pd.to_datetime(raw_dates[0]) if raw_dates else None

    event_row = None
    if raw_date_for_lookup is not None:
        match = events[(events["event_name"] == event_name) & (events["date"] == raw_date_for_lookup)]
        if not match.empty:
            event_row = match.iloc[0]

    # Top: event header cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Event", event_name)
    c2.metric("Trading Date Used", event_date)
    c3.metric("Curve Label", curve_label.replace("_", " "))
    c4.metric("Rows (assets)", str(len(df)))

    if event_row is not None:
        st.subheader("Event details (from events.csv)")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Raw date in CSV", event_row["date"].date().isoformat())
        d2.metric("Actual", "—" if pd.isna(event_row.get("actual")) else str(event_row.get("actual")))
        d3.metric("Forecast", "—" if pd.isna(event_row.get("forecast")) else str(event_row.get("forecast")))
        d4.metric("Previous", "—" if pd.isna(event_row.get("previous")) else str(event_row.get("previous")))
    else:
        st.info("No matching row found in events.csv for this selection (totally OK for now).")

    # Build a wide view for summary + easier reading
    wide = df.set_index("ticker")[["same_day_return", "next_day_return", "two_day_return"]].copy()

    # Charts
    st.subheader("Asset reactions")

    # Long format for charting
    plot_df = df[["ticker", "same_day_return", "next_day_return", "two_day_return"]].copy()
    plot_df = plot_df.melt(id_vars=["ticker"], var_name="window", value_name="return")
    if not show_two_day:
        plot_df = plot_df[plot_df["window"].isin(["same_day_return", "next_day_return"])]

    # Better labels
    window_label = {
        "same_day_return": "Same-day",
        "next_day_return": "Next-day",
        "two_day_return": "2-day cumulative",
    }
    plot_df["window"] = plot_df["window"].map(window_label)

    fig = px.bar(
        plot_df,
        x="ticker",
        y="return",
        color="window",
        barmode="group",
        title="Returns by asset",
    )
    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)

    # Summary paragraph
    st.subheader("Auto summary")
    st.markdown(make_summary(event_name, event_date, curve_label, wide))

    # Optional table
    if show_table:
        st.subheader("Returns table")
        table = df[[
            "ticker",
            "same_day_return",
            "next_day_return",
            "two_day_return",
            "same_day_z",
            "next_day_z",
        ]].copy()

        # Pretty formatting
        table["same_day_return"] = table["same_day_return"].apply(format_pct)
        table["next_day_return"] = table["next_day_return"].apply(format_pct)
        table["two_day_return"] = table["two_day_return"].apply(format_pct)
        table["same_day_z"] = table["same_day_z"].round(2)
        table["next_day_z"] = table["next_day_z"].round(2)

        st.dataframe(table, use_container_width=True)


if __name__ == "__main__":
    main()
