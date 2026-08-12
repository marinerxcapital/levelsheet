"""Interactive Brokers live data provider (optional, lazy import)."""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Literal

import pandas as pd
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from levelsheet.errors import ProviderUnavailableError
from levelsheet.models.schemas import validate_ohlc_df

_BAR_SIZE = {"1d": "1 day", "1wk": "1 week", "1mo": "1 month"}
_DURATION = {"1d": "3 Y", "1wk": "5 Y", "1mo": "10 Y"}


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
        self.host = os.environ.get("IB_HOST", host)
        self.port = int(os.environ.get("IB_PORT", str(port)))
        self.client_id = int(os.environ.get("IB_CLIENT_ID", str(client_id)))

    def is_available(self) -> bool:
        """True only when ib_insync imports, IB_ENABLED=true, and socket connects."""
        if os.environ.get(self.enabled_env, "").lower() != "true":
            return False
        try:
            from ib_insync import IB
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

    def _make_contract(self, symbol: str):  # type: ignore[no-untyped-def]
        from ib_insync import ContFuture

        from levelsheet.data.symbols import get_root_spec

        root = symbol.split("=")[0].split(":")[-1].upper()
        exchange = get_root_spec(root).exchange
        return ContFuture(root, exchange=exchange)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((TimeoutError, OSError, ConnectionError)),
        reraise=True,
    )
    def _req_historical(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        from ib_insync import IB, util

        ib = IB()
        try:
            ib.connect(self.host, self.port, clientId=self.client_id, timeout=5)
            contract = self._make_contract(symbol)
            ib.qualifyContracts(contract)
            # IB uses endDateTime + duration; request enough history then slice
            end_dt = datetime.combine(end, datetime.min.time())
            bars = ib.reqHistoricalData(
                contract,
                endDateTime=end_dt,
                durationStr=_DURATION[interval],
                barSizeSetting=_BAR_SIZE[interval],
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1,
            )
            if not bars:
                raise ProviderUnavailableError(f"IB returned no bars for {symbol}")
            df = util.df(bars)
        finally:
            if ib.isConnected():
                ib.disconnect()

        df = df.rename(
            columns={
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
        df = df.loc[(df.index.date >= start) & (df.index.date <= end)]
        df["volume"] = df["volume"].astype("Int64")
        df["contract"] = symbol
        for col in ("open", "high", "low", "close"):
            df[col] = df[col].astype("float64")
        keep = ["open", "high", "low", "close", "volume", "contract"]
        result: pd.DataFrame = df[keep]
        return result

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch historical bars via IB TWS/Gateway."""
        if not self.is_available():
            raise ProviderUnavailableError("IB provider unavailable")
        try:
            df = self._req_historical(symbol, start, end, interval)
        except ProviderUnavailableError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ProviderUnavailableError(f"IB historical fetch failed for {symbol}") from exc
        if df.empty:
            raise ProviderUnavailableError(f"IB returned empty data for {symbol}")
        validate_ohlc_df(df)
        logger.info("ib fetched {} rows for {}", len(df), symbol)
        return df
