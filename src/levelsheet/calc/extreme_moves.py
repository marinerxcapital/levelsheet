"""Extreme percentage move target calculations."""

from __future__ import annotations

from loguru import logger

EXTREME_MOVE_PCTS = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]


def extreme_move_targets(current_price: float) -> dict[str, float]:
    """Compute ±% extreme move targets from current_price."""
    up = {f"+{p}%": round(current_price * (1 + p / 100), 2) for p in EXTREME_MOVE_PCTS}
    down = {f"-{p}%": round(current_price * (1 - p / 100), 2) for p in EXTREME_MOVE_PCTS}
    result = up | down
    logger.debug("extreme_move_targets(current_price={}) -> {}", current_price, result)
    return result
