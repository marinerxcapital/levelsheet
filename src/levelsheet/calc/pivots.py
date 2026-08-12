"""Classic, Camarilla, and Woodie floor pivot calculations.

Implemented fully in Phase 1.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PivotSet(BaseModel):
    """Pivot levels container supporting classic/camarilla/woodie subsets."""

    p: float
    r1: float
    r2: float
    s1: float
    s2: float
    r3: Optional[float] = None
    s3: Optional[float] = None
    r4: Optional[float] = None
    s4: Optional[float] = None


def classic_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute classic floor pivots. Stub — implemented in Phase 1."""
    raise NotImplementedError("Phase 1")


def camarilla_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute Camarilla pivots. Stub — implemented in Phase 1."""
    raise NotImplementedError("Phase 1")


def woodie_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute Woodie pivots. Stub — implemented in Phase 1."""
    raise NotImplementedError("Phase 1")
