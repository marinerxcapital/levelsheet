"""SMA, EMA, and projected moving average calculations."""

from __future__ import annotations

import pandas as pd
from loguru import logger

from levelsheet.errors import InsufficientHistoryError


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple moving average with min_periods=length (leading NaNs)."""
    result = series.rolling(window=length, min_periods=length).mean()
    logger.debug("sma(length={}, n={}) -> last={}", length, len(series), result.iloc[-1] if len(result) else None)
    return result


def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential moving average (adjust=False, min_periods=length)."""
    result = series.ewm(span=length, adjust=False, min_periods=length).mean()
    logger.debug("ema(length={}, n={}) -> last={}", length, len(series), result.iloc[-1] if len(result) else None)
    return result


def projected_ma(ma_series: pd.Series) -> float:
    """Projected MA = current MA + slope(last two points) * 1.

    Raises:
        InsufficientHistoryError: fewer than 2 non-NaN MA values.
    """
    clean = ma_series.dropna()
    if len(clean) < 2:
        raise InsufficientHistoryError("projected_ma requires at least 2 non-NaN MA values")
    slope = float(ma_series.iloc[-1] - ma_series.iloc[-2])
    result = round(float(ma_series.iloc[-1] + slope), 2)
    logger.debug("projected_ma(last={}, prev={}) -> {}", ma_series.iloc[-1], ma_series.iloc[-2], result)
    return result
