"""Parquet cache layer with freshness policy and provider-chain fallback."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from loguru import logger

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.providers.base import DataProvider
from levelsheet.data.symbols import resolve_symbol
from levelsheet.errors import CacheError, ProviderUnavailableError
from levelsheet.models.schemas import validate_ohlc_df


class CachedDataFetcher:
    """Cache-aware OHLC fetcher with provider-chain fallback."""

    def __init__(self, providers: list[DataProvider], config: LevelSheetConfig) -> None:
        self.providers = providers
        self.config = config
        self.cache_dir = Path(config.data.cache.dir)
        self.max_staleness_hours = config.data.cache.max_staleness_hours
        self.last_source: str | None = None

    def _paths(self, root: str, interval: str) -> tuple[Path, Path]:
        base = self.cache_dir / root.upper()
        return base / f"{interval}.parquet", base / f"{interval}.meta.json"

    def _read_meta(self, meta_path: Path) -> dict[str, Any] | None:
        if not meta_path.exists():
            return None
        try:
            return json.loads(meta_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise CacheError(f"Corrupt meta {meta_path}") from exc

    def _write_cache(
        self, root: str, interval: str, df: pd.DataFrame, source: str
    ) -> None:
        parquet_path, meta_path = self._paths(root, interval)
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        out = df.copy()
        out.to_parquet(parquet_path, engine="pyarrow")
        meta = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "row_count": len(out),
            "min_date": out.index.min().isoformat(),
            "max_date": out.index.max().isoformat(),
        }
        meta_path.write_text(json.dumps(meta, indent=2))

    def _read_cache(self, root: str, interval: str) -> pd.DataFrame:
        parquet_path, _ = self._paths(root, interval)
        try:
            df = pd.read_parquet(parquet_path, engine="pyarrow")
        except Exception as exc:  # noqa: BLE001
            raise CacheError(f"Corrupt parquet {parquet_path}") from exc
        if not isinstance(df.index, pd.DatetimeIndex):
            if "date" in df.columns:
                df = df.set_index("date")
            df.index = pd.DatetimeIndex(pd.to_datetime(df.index))
        return df

    def _is_fresh(self, meta: dict[str, Any], as_of_date: date, df: pd.DataFrame) -> bool:
        max_cached = pd.Timestamp(df.index.max()).date()
        if as_of_date < max_cached:
            # Historical request — history doesn't change
            return True
        fetched_at = datetime.fromisoformat(meta["fetched_at"])
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600.0
        return age_hours <= self.max_staleness_hours

    def _fetch_from_providers(
        self, root: str, interval: Literal["1d", "1wk", "1mo"], start: date, end: date
    ) -> tuple[pd.DataFrame, str]:
        errors: list[str] = []
        for provider in self.providers:
            symbol = resolve_symbol(root, provider.name)
            logger.info("Trying provider={} for symbol={}", provider.name, symbol)
            try:
                df = provider.fetch_ohlc(symbol, start, end, interval)
                validate_ohlc_df(df)
                self.last_source = provider.name
                return df, provider.name
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{provider.name}: {exc}")
                logger.warning("Provider {} failed: {}", provider.name, exc)
        raise ProviderUnavailableError(
            f"All providers failed for {root}: {'; '.join(errors)}"
        )

    def fetch(
        self,
        root: str,
        interval: Literal["1d", "1wk", "1mo"],
        start: date,
        end: date,
        as_of_date: date,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Fetch with cache hit/miss/stale logic; self-heal on corruption."""
        parquet_path, meta_path = self._paths(root, interval)
        cached: pd.DataFrame | None = None
        meta: dict[str, Any] | None = None

        if parquet_path.exists() and not force_refresh:
            try:
                cached = self._read_cache(root, interval)
                meta = self._read_meta(meta_path)
                if meta and self._is_fresh(meta, as_of_date, cached):
                    self.last_source = str(meta.get("source", "cache"))
                    sliced = cached.loc[
                        (cached.index.date >= start) & (cached.index.date <= end)  # type: ignore[attr-defined]
                    ]
                    return sliced.copy()
            except CacheError as exc:
                logger.error("Cache corruption for {} {}: {}; refetching", root, interval, exc)
                try:
                    parquet_path.unlink(missing_ok=True)
                    meta_path.unlink(missing_ok=True)
                except OSError:
                    pass
                cached = None

        fresh, source = self._fetch_from_providers(root, interval, start, end)
        if cached is not None and not force_refresh:
            merged = pd.concat([cached, fresh])
            merged = merged[~merged.index.duplicated(keep="last")].sort_index()
        else:
            merged = fresh.sort_index()
        validate_ohlc_df(merged)
        self._write_cache(root, interval, merged, source)
        sliced = merged.loc[(merged.index.date >= start) & (merged.index.date <= end)]  # type: ignore[attr-defined]
        return sliced.copy()
