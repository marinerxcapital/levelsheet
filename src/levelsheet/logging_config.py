"""Loguru-based structured logging configuration for LevelSheet."""

from __future__ import annotations

import sys

from loguru import logger


def configure_logging(debug: bool = False) -> None:
    """Configure stderr + rotating JSON file logging.

    Args:
        debug: If True, set stderr level to DEBUG; otherwise INFO.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else "INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    logger.add(
        "logs/levelsheet.log",
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        serialize=True,
        enqueue=True,
    )
