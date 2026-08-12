"""Fibonacci retracement and extension level calculations."""

from __future__ import annotations

from typing import Literal

from loguru import logger

RETRACEMENT_RATIOS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.764, 1.0]
EXTENSION_RATIOS = [1.272, 1.618, 2.0, 2.618]


def fibonacci_levels(
    swing_high: float, swing_low: float, direction: Literal["up", "down"]
) -> dict[str, float]:
    """Compute fibonacci retracement and extension levels.

    For direction=\"down\" (retracing a prior up-swing):
        retracement price = swing_high - rng * r
        extension price   = swing_low  - rng * (r - 1)
    For direction=\"up\" the formulas are mirrored from swing_low / swing_high.
    """
    rng = swing_high - swing_low
    levels: dict[str, float] = {}
    for r in RETRACEMENT_RATIOS:
        price = swing_high - rng * r if direction == "down" else swing_low + rng * r
        levels[f"{r*100:.1f}%"] = round(price, 2)
    for r in EXTENSION_RATIOS:
        price = swing_low - rng * (r - 1) if direction == "down" else swing_high + rng * (r - 1)
        levels[f"{r*100:.1f}%"] = round(price, 2)
    logger.debug(
        "fibonacci_levels(swing_high={}, swing_low={}, direction={}) -> {}",
        swing_high,
        swing_low,
        direction,
        levels,
    )
    return levels
