"""Price vs MA bias classification (LONG/SHORT/NONE).

Implemented fully in Phase 1.
"""

from __future__ import annotations

from typing import Literal


def bias(close: float, ma_value: float) -> Literal["LONG", "SHORT", "NONE"]:
    """Classify close relative to MA. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
