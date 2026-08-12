"""Integration test: provider chain fallback Polygon → yfinance."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.cache import CachedDataFetcher
from levelsheet.errors import ProviderUnavailableError


def _sample_df() -> pd.DataFrame:
    idx = pd.date_range("2024-06-03", periods=5, freq="B")
    df = pd.DataFrame(
        {
            "open": [5000.0, 5010, 5020, 5015, 5030],
            "high": [5015.0, 5025, 5035, 5030, 5045],
            "low": [4990.0, 5000, 5010, 5005, 5020],
            "close": [5010.0, 5020, 5015, 5030, 5040],
            "volume": pd.Series([100, 110, 120, 130, 140], dtype="Int64"),
            "contract": ["ES=F"] * 5,
        },
        index=idx,
    )
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


class FailingPolygon:
    name = "polygon"

    def is_available(self) -> bool:
        return True

    def fetch_ohlc(self, symbol: str, start: date, end: date, interval: str) -> pd.DataFrame:
        raise ProviderUnavailableError("polygon down")


class OkYFinance:
    name = "yfinance"

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.called = False

    def is_available(self) -> bool:
        return True

    def fetch_ohlc(self, symbol: str, start: date, end: date, interval: str) -> pd.DataFrame:
        self.called = True
        return self.df.copy()


def test_provider_fallback_to_yfinance(tmp_path: Path) -> None:
    df = _sample_df()
    yf = OkYFinance(df)
    cfg = LevelSheetConfig()
    cfg.data.cache.dir = str(tmp_path / "cache")
    fetcher = CachedDataFetcher([FailingPolygon(), yf], cfg)
    start, end = df.index.min().date(), df.index.max().date()
    out = fetcher.fetch("ES", "1d", start, end, as_of_date=end, force_refresh=True)
    assert yf.called is True
    assert len(out) == 5
    meta = json.loads((tmp_path / "cache" / "ES" / "1d.meta.json").read_text())
    assert meta["source"] == "yfinance"
