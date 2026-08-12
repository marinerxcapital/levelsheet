#!/usr/bin/env python3
"""Pre-warm Parquet cache for every root in config.symbols.default_list."""

from __future__ import annotations

from datetime import date, timedelta

from loguru import logger

from levelsheet.config.loader import load_config
from levelsheet.data.cache import CachedDataFetcher
from levelsheet.data.providers import get_provider_chain
from levelsheet.logging_config import configure_logging


def main() -> None:
    """Bootstrap cache for default symbols across 1d/1wk/1mo."""
    configure_logging()
    config = load_config()
    providers = get_provider_chain(config)
    fetcher = CachedDataFetcher(providers, config)
    end = date.today()
    start = end - timedelta(days=365 * 3)
    for root in config.symbols.default_list:
        for interval in ("1d", "1wk", "1mo"):
            try:
                df = fetcher.fetch(
                    root, interval, start, end, as_of_date=end, force_refresh=True  # type: ignore[arg-type]
                )
                logger.info("Warmed {} {} -> {} rows", root, interval, len(df))
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed warming {} {}: {}", root, interval, exc)


if __name__ == "__main__":
    main()
