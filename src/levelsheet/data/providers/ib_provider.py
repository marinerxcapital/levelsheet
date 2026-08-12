"""Interactive Brokers live data provider (optional, lazy import). Stub — Phase 2."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd


class IBProvider:
    """Optional IB TWS/Gateway provider; never a hard dependency."""

    name: str = "ib"

    def __init__(
        self,
        enabled_env: str = "IB_ENABLED",
        host: str = "127.0.0.1",
        port: int = 7497,
        client_id: int = 1,
    ) -> None:
        self.enabled_env = enabled_env
        self.host = host
        self.port = port
        self.client_id = client_id

    def is_available(self) -> bool:
        """True only when ib_insync imports, IB_ENABLED=true, and socket connects. Stub."""
        raise NotImplementedError("Phase 2")

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch historical bars via IB. Stub — Phase 2."""
        raise NotImplementedError("Phase 2")
