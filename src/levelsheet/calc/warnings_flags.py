"""Intraday warning flags: false day, RTH gap, BLUD, AHDD."""

from __future__ import annotations

from loguru import logger
from pydantic import BaseModel


class OHLCBar(BaseModel):
    """Single OHLC bar for warning flag evaluation."""

    open: float
    high: float
    low: float
    close: float


def is_false_day(today: OHLCBar, yesterday: OHLCBar) -> bool:
    """True if today's open is outside yesterday's range but close is back inside."""
    opened_outside = today.open > yesterday.high or today.open < yesterday.low
    closed_inside = yesterday.low <= today.close <= yesterday.high
    result = opened_outside and closed_inside
    logger.debug("is_false_day -> {}", result)
    return result


def is_rth_gap(today_open: float, prev_close: float, threshold_pct: float = 0.15) -> bool:
    """Detect RTH gap at or above threshold_pct."""
    result = abs(today_open - prev_close) / prev_close * 100 >= threshold_pct
    logger.debug("is_rth_gap(open={}, prev_close={}) -> {}", today_open, prev_close, result)
    return result


def is_blud(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Big Low Up Day: undercuts yesterday's low, closes green near day's high."""
    undercut_low = today.low < yesterday.low
    closed_green = today.close > today.open
    day_range = today.high - today.low
    near_high = (
        day_range > 0 and (today.high - today.close) / day_range * 100 <= close_proximity_pct
    )
    result = undercut_low and closed_green and near_high
    logger.debug("is_blud -> {}", result)
    return result


def is_ahdd(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Above High Down Day: exceeds yesterday's high, closes red near day's low."""
    exceeded_high = today.high > yesterday.high
    closed_red = today.close < today.open
    day_range = today.high - today.low
    near_low = day_range > 0 and (today.close - today.low) / day_range * 100 <= close_proximity_pct
    result = exceeded_high and closed_red and near_low
    logger.debug("is_ahdd -> {}", result)
    return result
