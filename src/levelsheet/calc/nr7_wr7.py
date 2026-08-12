"""Narrow Range 7 / Wide Range 7 day detection."""

from __future__ import annotations

import pandas as pd
from loguru import logger

from levelsheet.errors import InsufficientHistoryError


def is_nr7(df: pd.DataFrame) -> bool:
    """True if the latest bar has the narrowest range of the last 7."""
    ranges = (df["high"] - df["low"]).tail(7)
    if len(ranges) < 7:
        raise InsufficientHistoryError("NR7 requires 7 bars")
    result = bool(ranges.iloc[-1] == ranges.min())
    logger.debug("is_nr7 -> {}", result)
    return result


def is_wr7(df: pd.DataFrame) -> bool:
    """True if the latest bar has the widest range of the last 7."""
    ranges = (df["high"] - df["low"]).tail(7)
    if len(ranges) < 7:
        raise InsufficientHistoryError("WR7 requires 7 bars")
    result = bool(ranges.iloc[-1] == ranges.max())
    logger.debug("is_wr7 -> {}", result)
    return result
