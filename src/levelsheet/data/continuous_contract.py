"""Ratio-adjusted continuous futures contract construction. Stub — Phase 2."""

from __future__ import annotations

from datetime import date

import pandas as pd

from levelsheet.data.providers.base import DataProvider


def build_continuous_series(
    root: str, provider: DataProvider, start: date, end: date
) -> pd.DataFrame:
    """Build ratio-adjusted continuous OHLC series. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")
