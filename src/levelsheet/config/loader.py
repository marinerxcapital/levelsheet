"""Configuration loader with merge precedence chain.

Merge order (lowest → highest):
  LevelSheetConfig defaults → default_config.yaml → ~/.levelsheet/config.yaml
  → ./levelsheet.yaml → cli_overrides → LEVELSHEET__* environment variables.
"""

from __future__ import annotations

from typing import Any

from levelsheet.config.schema import LevelSheetConfig


def load_config(cli_overrides: dict[str, Any] | None = None) -> LevelSheetConfig:
    """Load and merge configuration from all sources.

    Args:
        cli_overrides: Optional dict of CLI argparse namespace values (None values ignored).

    Returns:
        Fully validated LevelSheetConfig.

    Note:
        Full merge implementation lands in Phase 6; Phase 0 returns defaults.
    """
    _ = cli_overrides
    return LevelSheetConfig()
