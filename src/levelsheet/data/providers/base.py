"""DataProvider protocol. Implemented in Phase 2."""

from __future__ import annotations

from datetime import date
from typing import Literal, Protocol

import pandas as pd


class DataProvider(Protocol):
    """Protocol for OHLC data providers."""

    name: str

    def is_available(self) -> bool:
        """Return True if this provider can be used."""
        ...

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch OHLC data conforming to the canonical schema."""
        ...
