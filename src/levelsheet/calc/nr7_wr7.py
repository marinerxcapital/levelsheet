"""Narrow Range 7 / Wide Range 7 day detection.

Implemented fully in Phase 1.
"""

from __future__ import annotations

import pandas as pd


def is_nr7(df: pd.DataFrame) -> bool:
    """True if the latest bar has the narrowest range of the last 7. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")


def is_wr7(df: pd.DataFrame) -> bool:
    """True if the latest bar has the widest range of the last 7. Stub — Phase 1."""
    raise NotImplementedError("Phase 1")
