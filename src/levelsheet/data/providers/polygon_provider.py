"""Polygon.io data provider. Stub — Phase 2."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd


class PolygonProvider:
    """Paid primary OHLC provider via Polygon REST API."""

    name: str = "polygon"

    def __init__(self, api_key_env: str = "POLYGON_API_KEY") -> None:
        self.api_key_env = api_key_env

    def is_available(self) -> bool:
        """True when POLYGON_API_KEY is set. Stub — Phase 2."""
        raise NotImplementedError("Phase 2")

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch aggregates via Polygon. Stub — Phase 2."""
        raise NotImplementedError("Phase 2")
