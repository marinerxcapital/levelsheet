"""Canonical OHLC DataFrame validation and sheet data models."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field

from levelsheet.calc.autotrade import AutoTradeSettings
from levelsheet.calc.elliott_wave import ElliottProjection
from levelsheet.calc.pivots import PivotSet
from levelsheet.calc.warnings_flags import OHLCBar
from levelsheet.errors import DataValidationError


def validate_ohlc_df(df: pd.DataFrame) -> None:
    """Validate canonical OHLC schema; raise DataValidationError on violation."""
    required = ["open", "high", "low", "close", "volume", "contract"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise DataValidationError(f"Missing columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise DataValidationError("Index must be a DatetimeIndex")
    if df.index.tz is not None:
        raise DataValidationError("Index must be tz-naive")
    if not df.index.is_monotonic_increasing:
        raise DataValidationError("Index must be sorted ascending")
    if df.index.duplicated().any():
        raise DataValidationError("Index has duplicate dates")
    for col in ("open", "high", "low", "close"):
        if df[col].isna().any():
            raise DataValidationError(f"NaN in {col}")
        if (df[col] <= 0).any():
            raise DataValidationError(f"{col} must be > 0")
    if (df["high"] < df["low"]).any():
        raise DataValidationError("high < low")
    if (df["high"] < df["open"]).any() or (df["high"] < df["close"]).any():
        raise DataValidationError("high must be >= open and close")
    if (df["low"] > df["open"]).any() or (df["low"] > df["close"]).any():
        raise DataValidationError("low must be <= open and close")


class SheetData(BaseModel):
    """Fully computed payload for one levels sheet render."""

    root: str
    as_of_date: str
    contract: str = ""
    days_to_roll: int = 999
    decimals: int = 2
    company_name: str = "BPTC 26 LLC"
    footer_text: str = "For educational purposes only. Not financial advice."
    logo_path: Optional[str] = None

    daily_pivots: Optional[PivotSet] = None
    weekly_pivots: Optional[PivotSet] = None
    monthly_pivots: Optional[PivotSet] = None
    today_bar: Optional[OHLCBar] = None
    ma_values: dict[int, float] = Field(default_factory=dict)
    ma_bias: dict[int, str] = Field(default_factory=dict)
    atr_value: Optional[float] = None
    atr_5d: Optional[float] = None
    nr7: bool = False
    wr7: bool = False
    hi_7: Optional[float] = None
    lo_7: Optional[float] = None
    hi_20: Optional[float] = None
    lo_20: Optional[float] = None
    long_term_fib: dict[str, float] = Field(default_factory=dict)
    daily_fib: dict[str, float] = Field(default_factory=dict)
    extreme_moves: dict[str, float] = Field(default_factory=dict)
    autotrade: Optional[AutoTradeSettings] = None
    elliott: Optional[ElliottProjection] = None
    projected_mas: dict[int, tuple[float, float]] = Field(default_factory=dict)
    warnings: dict[str, bool] = Field(default_factory=dict)
    extras: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}
