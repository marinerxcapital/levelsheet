"""True Range and Wilder ATR calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from loguru import logger


def true_range(df: pd.DataFrame) -> pd.Series:
    """Compute True Range: max(H-L, |H-prev_C|, |L-prev_C|)."""
    prev_close = df["close"].shift(1)
    a = df["high"] - df["low"]
    b = (df["high"] - prev_close).abs()
    c = (df["low"] - prev_close).abs()
    result = pd.concat([a, b, c], axis=1).max(axis=1)
    logger.debug("true_range(n={}) -> last={}", len(df), result.iloc[-1] if len(result) else None)
    return result


def atr_wilder(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Wilder's smoothed Average True Range.

    Seed ATR[length-1] = mean(TR[:length]); thereafter
    ATR[i] = (ATR[i-1] * (length-1) + TR[i]) / length.
    """
    tr = true_range(df)
    atr = pd.Series(index=df.index, dtype="float64")
    if len(tr) < length:
        atr[:] = np.nan
        return atr
    atr.iloc[:length] = np.nan
    atr.iloc[length - 1] = tr.iloc[:length].mean()
    for i in range(length, len(tr)):
        atr.iloc[i] = (atr.iloc[i - 1] * (length - 1) + tr.iloc[i]) / length
    logger.debug("atr_wilder(length={}, n={}) -> last={}", length, len(df), atr.iloc[-1])
    return atr
