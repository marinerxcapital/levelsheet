#!/usr/bin/env python3
"""Pre-warm Parquet cache for every root in config.symbols.default_list.

Intended for nightly cron / GitHub Action. Fully wired in Phase 2/5.
"""

from __future__ import annotations

from loguru import logger

from levelsheet.config.loader import load_config
from levelsheet.logging_config import configure_logging


def main() -> None:
    """Bootstrap cache for default symbols across 1d/1wk/1mo."""
    configure_logging()
    config = load_config()
    logger.info(
        "bootstrap_cache stub — will warm {} roots in Phase 2/5",
        config.symbols.default_list,
    )


if __name__ == "__main__":
    main()
