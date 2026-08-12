"""Interactive Brokers live data provider (optional, lazy import)."""

from __future__ import annotations

import os
from datetime import date
from typing import Literal

import pandas as pd
from loguru import logger

from levelsheet.errors import ProviderUnavailableError


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
        """True only when ib_insync imports, IB_ENABLED=true, and socket connects."""
        if os.environ.get(self.enabled_env, "").lower() != "true":
            return False
        try:
            from ib_insync import IB  # type: ignore[import-untyped]
        except ImportError:
            return False
        ib = IB()
        try:
            ib.connect(self.host, self.port, clientId=self.client_id, timeout=2)
            ok = ib.isConnected()
            ib.disconnect()
            return bool(ok)
        except Exception:  # noqa: BLE001
            return False

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch historical bars via IB."""
        if not self.is_available():
            raise ProviderUnavailableError("IB provider unavailable")
        raise ProviderUnavailableError(
            f"IB historical fetch not configured for {symbol} [{start},{end}] {interval}"
        )
