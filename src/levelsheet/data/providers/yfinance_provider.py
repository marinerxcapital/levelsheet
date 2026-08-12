"""YFinance data provider."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd
import requests
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from levelsheet.data.symbols import resolve_symbol
from levelsheet.errors import ProviderUnavailableError
from levelsheet.models.schemas import validate_ohlc_df

_INTERVAL_MAP = {"1d": "1d", "1wk": "1wk", "1mo": "1mo"}


class YFinanceProvider:
    """Always-available free fallback OHLC provider via yfinance."""

    name: str = "yfinance"

    def is_available(self) -> bool:
        """Always True for yfinance."""
        return True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((requests.RequestException, TimeoutError)),
        reraise=True,
    )
    def _download(
        self, ticker: str, start: date, end: date, interval: str
    ) -> pd.DataFrame:
        import yfinance as yf

        return yf.download(
            ticker,
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            progress=False,
            auto_adjust=False,
        )

    def fetch_ohlc(
        self, symbol: str, start: date, end: date, interval: Literal["1d", "1wk", "1mo"]
    ) -> pd.DataFrame:
        """Download OHLC via yfinance and normalize to canonical schema."""
        ticker = resolve_symbol(symbol, "yfinance") if "=" not in symbol else symbol
        try:
            raw = self._download(ticker, start, end, _INTERVAL_MAP[interval])
        except Exception as exc:  # noqa: BLE001
            raise ProviderUnavailableError(f"yfinance failed for {ticker}") from exc
        if raw is None or raw.empty:
            raise ProviderUnavailableError(f"yfinance returned empty data for {ticker}")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] for c in raw.columns]
        df = raw.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        keep = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
        df = df[keep].copy()
        df.index = pd.DatetimeIndex(pd.to_datetime(df.index).tz_localize(None)).normalize()
        df = df.sort_index()
        df = df[~df.index.duplicated(keep="last")]
        if "volume" not in df.columns:
            df["volume"] = pd.Series([pd.NA] * len(df), dtype="Int64")
        else:
            df["volume"] = df["volume"].astype("Int64")
        df["contract"] = ticker
        for col in ("open", "high", "low", "close"):
            df[col] = df[col].astype("float64")
        validate_ohlc_df(df)
        logger.info("yfinance fetched {} rows for {}", len(df), ticker)
        return df
