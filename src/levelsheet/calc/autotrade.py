"""Auto-trade stop/trail/target settings from ATR.

Implemented fully in Phase 1.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from levelsheet.config.schema import AutoTradeConfig


class AutoTradeSettings(BaseModel):
    """Computed auto-trade risk settings for a sheet."""

    max_stop: float
    trail: float
    frequency: str
    max_target: float
    side: Literal["BOTH", "LONG", "SHORT"]
    size: int
    scale_out: float
    max_risk_dollars: float


def compute_autotrade_settings(
    atr_value: float, root: str, config: AutoTradeConfig, point_value: float
) -> AutoTradeSettings:
    """Compute auto-trade settings from ATR. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
