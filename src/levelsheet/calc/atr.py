"""True Range and Wilder ATR calculations.

Implemented fully in Phase 1.
"""

from __future__ import annotations

import pandas as pd


def true_range(df: pd.DataFrame) -> pd.Series:
    """Compute True Range series. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def atr_wilder(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Wilder's smoothed ATR. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
