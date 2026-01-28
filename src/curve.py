# src/curve.py
from __future__ import annotations
import pandas as pd


def classify_curve_move(shy_ret: float, tlt_ret: float) -> str:
    """
    ETF price returns as yield proxies:
      price down => yields up
      price up   => yields down
    """
    if pd.isna(shy_ret) or pd.isna(tlt_ret):
        return "unknown"

    # Bear move (yields up): both prices down
    if shy_ret < 0 and tlt_ret < 0:
        return "bear_steepening" if tlt_ret < shy_ret else "bear_flattening"

    # Bull move (yields down): both prices up
    if shy_ret > 0 and tlt_ret > 0:
        return "bull_steepening" if tlt_ret > shy_ret else "bull_flattening"

    # Mixed directions
    return "twist"
