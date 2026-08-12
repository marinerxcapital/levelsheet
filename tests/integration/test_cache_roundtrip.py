"""Integration test: cache roundtrip and self-healing corruption recovery."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.cache import CachedDataFetcher


class FakeProvider:
    name = "fake"
    calls = 0

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def is_available(self) -> bool:
        return True

    def fetch_ohlc(self, symbol: str, start: date, end: date, interval: str) -> pd.DataFrame:
        FakeProvider.calls += 1
        return self.df.copy()


def _sample_df(n: int = 10) -> pd.DataFrame:
    idx = pd.date_range("2024-01-02", periods=n, freq="B")
    rows = []
    price = 5000.0
    for i in range(n):
        o, h, low, c = price, price + 10, price - 10, price + 5
        rows.append(
            {
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "volume": 1000 + i,
                "contract": "ESH24",
            }
        )
        price = c
    df = pd.DataFrame(rows, index=idx)
    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    df["volume"] = df["volume"].astype("Int64")
    return df


def test_cache_roundtrip(tmp_path: Path) -> None:
    FakeProvider.calls = 0
    df = _sample_df()
    cfg = LevelSheetConfig()
    cfg.data.cache.dir = str(tmp_path / "cache")
    fetcher = CachedDataFetcher([FakeProvider(df)], cfg)
    start, end = df.index.min().date(), df.index.max().date()
    out1 = fetcher.fetch("ES", "1d", start, end, as_of_date=start, force_refresh=True)
    out2 = fetcher.fetch("ES", "1d", start, end, as_of_date=start, force_refresh=False)
    # Parquet round-trip may drop freq metadata; compare values.
    out1.index.freq = None
    out2.index.freq = None
    pd.testing.assert_frame_equal(out1, out2, check_dtype=False, check_freq=False)
    assert FakeProvider.calls == 1  # second call served from cache


def test_cache_corruption_self_heals(tmp_path: Path) -> None:
    FakeProvider.calls = 0
    df = _sample_df()
    cfg = LevelSheetConfig()
    cache_dir = tmp_path / "cache"
    cfg.data.cache.dir = str(cache_dir)
    fetcher = CachedDataFetcher([FakeProvider(df)], cfg)
    start, end = df.index.min().date(), df.index.max().date()
    fetcher.fetch("ES", "1d", start, end, as_of_date=start, force_refresh=True)
    parquet = cache_dir / "ES" / "1d.parquet"
    parquet.write_bytes(b"not-a-parquet-file!!!")
    FakeProvider.calls = 0
    out = fetcher.fetch("ES", "1d", start, end, as_of_date=start, force_refresh=False)
    assert len(out) == len(df)
    assert FakeProvider.calls == 1
