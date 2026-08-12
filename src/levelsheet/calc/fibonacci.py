"""Fibonacci retracement and extension level calculations.

Implemented fully in Phase 1.
"""

from __future__ import annotations

from typing import Literal

RETRACEMENT_RATIOS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.764, 1.0]
EXTENSION_RATIOS = [1.272, 1.618, 2.0, 2.618]


def fibonacci_levels(
    swing_high: float, swing_low: float, direction: Literal["up", "down"]
) -> dict[str, float]:
    """Compute fibonacci retracement and extension levels. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
