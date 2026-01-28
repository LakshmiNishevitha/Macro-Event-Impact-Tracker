from __future__ import annotations

import numpy as np
import pandas as pd


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily returns: r_t = P_t / P_{t-1} - 1"""
    return prices.pct_change()


def rolling_zscore(returns: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """z = return / rolling_std(window)"""
    vol = returns.rolling(window).std()
    return returns / vol


def map_to_trading_day(event_date: pd.Timestamp, trading_days: pd.DatetimeIndex) -> pd.Timestamp:
    """If event date isn't a trading day, map to the next trading day."""
    event_date = pd.to_datetime(event_date).normalize()
    if event_date in trading_days:
        return event_date
    pos = trading_days.searchsorted(event_date)
    if pos >= len(trading_days):
        return trading_days[-1]
    return trading_days[pos]


def compute_event_impacts(
    events: pd.DataFrame,
    prices: pd.DataFrame,
    z_window: int = 60,
) -> pd.DataFrame:
    returns = compute_returns(prices)
    z = rolling_zscore(returns, window=z_window)

    trading_days = prices.index
    out_rows = []

    for _, ev in events.iterrows():
        raw_date = ev["date"]
        t0 = map_to_trading_day(raw_date, trading_days)

        if t0 not in trading_days:
            continue
        i0 = trading_days.get_loc(t0)

        if i0 == 0 or i0 >= len(trading_days) - 1:
            continue

        t_minus_1 = trading_days[i0 - 1]
        t_plus_1 = trading_days[i0 + 1]

        for ticker in prices.columns:
            same_day = returns.at[t0, ticker]
            next_day = returns.at[t_plus_1, ticker]
            two_day = (1 + same_day) * (1 + next_day) - 1

            out_rows.append(
                {
                    "event_name": ev.get("event_name"),
                    "country": ev.get("country"),
                    "event_date_raw": pd.to_datetime(raw_date).date().isoformat(),
                    "event_date_trading": t0.date().isoformat(),
                    "t_minus_1": t_minus_1.date().isoformat(),
                    "t_plus_1": t_plus_1.date().isoformat(),
                    "ticker": ticker,
                    "same_day_return": float(same_day) if pd.notna(same_day) else np.nan,
                    "next_day_return": float(next_day) if pd.notna(next_day) else np.nan,
                    "two_day_return": float(two_day) if pd.notna(two_day) else np.nan,
                    "same_day_z": float(z.at[t0, ticker]) if pd.notna(z.at[t0, ticker]) else np.nan,
                    "next_day_z": float(z.at[t_plus_1, ticker]) if pd.notna(z.at[t_plus_1, ticker]) else np.nan,
                }
            )

    impacts = pd.DataFrame(out_rows)
    if not impacts.empty:
        impacts = impacts.sort_values(["event_date_trading", "event_name", "ticker"]).reset_index(drop=True)
    return impacts