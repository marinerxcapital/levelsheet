"""SMA, EMA, and projected moving average calculations.

Implemented fully in Phase 1.
"""

from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple moving average. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential moving average. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def projected_ma(ma_series: pd.Series) -> float:
    """Project next MA value from last two points. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
