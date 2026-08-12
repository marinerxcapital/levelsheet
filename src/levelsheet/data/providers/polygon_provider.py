"""Polygon.io data provider."""

from __future__ import annotations

import os
from datetime import date
from typing import Any, Literal

import pandas as pd
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from levelsheet.data.symbols import resolve_symbol
from levelsheet.errors import ProviderUnavailableError
from levelsheet.models.schemas import validate_ohlc_df

_TIMESPAN = {"1d": "day", "1wk": "week", "1mo": "month"}


class PolygonProvider:
    """Paid primary OHLC provider via Polygon REST API."""

    name: str = "polygon"

    def __init__(self, api_key_env: str = "POLYGON_API_KEY") -> None:
        self.api_key_env = api_key_env

    def is_available(self) -> bool:
        """True when POLYGON_API_KEY is set and non-empty."""
        key = os.environ.get(self.api_key_env, "")
        return bool(key and key.strip())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((TimeoutError, OSError)),
        reraise=True,
    )
    def _get_aggs(
        self, ticker: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> list[Any]:
        from polygon import RESTClient

        api_key = os.environ[self.api_key_env]
        client = RESTClient(api_key)
        return list(
            client.get_aggs(
                ticker,
                1,
                _TIMESPAN[interval],
                from_=start.isoformat(),
                to=end.isoformat(),
            )
        )

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Fetch aggregates via Polygon and normalize to canonical schema."""
        if not self.is_available():
            raise ProviderUnavailableError("POLYGON_API_KEY not set")
        ticker = resolve_symbol(symbol, "polygon") if ":" not in symbol else symbol
        try:
            aggs = self._get_aggs(ticker, start, end, interval)
        except Exception as exc:  # noqa: BLE001
            raise ProviderUnavailableError(f"polygon failed for {ticker}") from exc
        if not aggs:
            raise ProviderUnavailableError(f"polygon returned empty data for {ticker}")
        rows: list[dict[str, Any]] = []
        for a in aggs:
            ts = pd.Timestamp(int(getattr(a, "timestamp")), unit="ms").normalize()
            rows.append(
                {
                    "date": ts,
                    "open": float(a.open),
                    "high": float(a.high),
                    "low": float(a.low),
                    "close": float(a.close),
                    "volume": int(getattr(a, "volume", 0) or 0),
                    "contract": str(getattr(a, "otc", None) or ticker),
                }
            )
        df = pd.DataFrame(rows).set_index("date").sort_index()
        df.index = pd.DatetimeIndex(df.index).tz_localize(None)
        df["volume"] = df["volume"].astype("Int64")
        df["contract"] = df["contract"].astype(str)
        validate_ohlc_df(df)
        logger.info("polygon fetched {} rows for {}", len(df), ticker)
        return df
