"""Auto-trade stop/trail/target settings from ATR."""

from __future__ import annotations

from typing import Literal

from loguru import logger
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
    """Compute auto-trade settings from ATR and root point value."""
    max_stop = round(atr_value * config.stop_atr_mult, 2)
    result = AutoTradeSettings(
        max_stop=max_stop,
        trail=round(atr_value * config.trail_atr_mult, 2),
        frequency=config.frequency,
        max_target=round(atr_value * config.target_atr_mult, 2),
        side=config.side,
        size=config.contracts,
        scale_out=config.scale_out_pct,
        max_risk_dollars=round(max_stop * point_value * config.contracts, 2),
    )
    logger.debug(
        "compute_autotrade_settings(atr={}, root={}, point_value={}) -> {}",
        atr_value,
        root,
        point_value,
        result,
    )
    return result
