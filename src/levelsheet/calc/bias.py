"""Price vs MA bias classification (LONG/SHORT/NONE)."""

from __future__ import annotations

from typing import Literal

import pandas as pd
from loguru import logger


def bias(close: float, ma_value: float) -> Literal["LONG", "SHORT", "NONE"]:
    """Classify close relative to MA value."""
    if pd.isna(ma_value):
        result: Literal["LONG", "SHORT", "NONE"] = "NONE"
    elif close > ma_value:
        result = "LONG"
    elif close < ma_value:
        result = "SHORT"
    else:
        result = "NONE"
    logger.debug("bias(close={}, ma_value={}) -> {}", close, ma_value, result)
    return result
