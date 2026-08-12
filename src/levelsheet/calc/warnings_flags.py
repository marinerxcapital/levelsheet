"""Intraday warning flags: false day, RTH gap, BLUD, AHDD.

Implemented fully in Phase 1.
"""

from __future__ import annotations

from pydantic import BaseModel


class OHLCBar(BaseModel):
    """Single OHLC bar for warning flag evaluation."""

    open: float
    high: float
    low: float
    close: float


def is_false_day(today: OHLCBar, yesterday: OHLCBar) -> bool:
    """Detect false-day failed breakout. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def is_rth_gap(today_open: float, prev_close: float, threshold_pct: float = 0.15) -> bool:
    """Detect RTH gap above threshold. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def is_blud(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Detect Big Low Up Day. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def is_ahdd(today: OHLCBar, yesterday: OHLCBar, close_proximity_pct: float = 25.0) -> bool:
    """Detect Above High Down Day. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
