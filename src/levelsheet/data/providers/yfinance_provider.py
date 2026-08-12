"""YFinance data provider. Stub — Phase 2."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd


class YFinanceProvider:
    """Always-available free fallback OHLC provider via yfinance."""

    name: str = "yfinance"

    def is_available(self) -> bool:
        """Always True for yfinance."""
        raise NotImplementedError("Phase 2")

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Download OHLC via yfinance. Stub — Phase 2."""
        raise NotImplementedError("Phase 2")
