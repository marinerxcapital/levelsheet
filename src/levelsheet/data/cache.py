"""Parquet cache layer with freshness policy. Stub — Phase 2."""

from __future__ import annotations

from datetime import date
from typing import Literal

import pandas as pd

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.providers.base import DataProvider


class CachedDataFetcher:
    """Cache-aware OHLC fetcher with provider-chain fallback."""

    def __init__(self, providers: list[DataProvider], config: LevelSheetConfig) -> None:
        self.providers = providers
        self.config = config

    def fetch(
        self,
        root: str,
        interval: Literal["1d", "1wk", "1mo"],
        start: date,
        end: date,
        as_of_date: date,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Fetch with cache hit/miss/stale logic. Stub — Phase 2."""
        raise NotImplementedError("Phase 2")
