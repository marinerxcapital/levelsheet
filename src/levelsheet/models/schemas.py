"""Canonical OHLC DataFrame validation and sheet data models.

validate_ohlc_df implemented in Phase 2; SheetData assembled in Phase 3/5.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field


def validate_ohlc_df(df: pd.DataFrame) -> None:
    """Validate canonical OHLC schema. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


class SheetData(BaseModel):
    """Fully computed payload for one levels sheet render."""

    root: str
    as_of_date: str
    contract: str = ""
    days_to_roll: int = 999
    decimals: int = 2
    # Raw panels populate these; defaults keep Phase 0 importable.
    extras: dict[str, Any] = Field(default_factory=dict)
    company_name: str = "BPTC 26 LLC"
    footer_text: str = "For educational purposes only. Not financial advice."
    logo_path: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}
