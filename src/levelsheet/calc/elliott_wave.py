"""Simplified Elliott Wave zigzag detection and Wave-5 projection.

Implemented fully in Phase 1.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from pydantic import BaseModel


class ElliottProjection(BaseModel):
    """Elliott wave projection result."""

    waves: list[dict[str, object]]
    ext_ratio: float
    wave5_target: float
    extended_third: Optional[bool] = None


def detect_swings_zigzag(df: pd.DataFrame, threshold_pct: float = 3.0) -> pd.DataFrame:
    """Percentage zigzag swing detection. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def elliott_wave_projection(swings: pd.DataFrame) -> ElliottProjection:
    """Project Wave 5 target from last 6 swing points. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
