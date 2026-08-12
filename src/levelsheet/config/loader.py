"""Configuration loader with merge precedence chain.

Merge order (lowest → highest):
  LevelSheetConfig defaults → default_config.yaml → ~/.levelsheet/config.yaml
  → ./levelsheet.yaml → cli_overrides → LEVELSHEET__* environment variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.errors import ConfigError


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base; override wins."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text()) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"Config file {path} must be a mapping")
        return data
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}") from exc


def _package_default_yaml() -> Path:
    return Path(__file__).parent / "default_config.yaml"


def _cli_to_config_dict(cli_overrides: dict[str, Any] | None) -> dict[str, Any]:
    """Map relevant CLI args into nested config overrides (only non-None dicts)."""
    if not cli_overrides:
        return {}
    out: dict[str, Any] = {}
    for key in (
        "symbols",
        "pivots",
        "moving_averages",
        "fibonacci",
        "elliott_wave",
        "atr",
        "autotrade",
        "extreme_moves",
        "warnings",
        "theme",
        "branding",
        "data",
        "render",
        "plugins",
    ):
        val = cli_overrides.get(key)
        # Argparse also uses names like `symbols` for positional lists — only merge dicts.
        if isinstance(val, dict):
            out[key] = val
    return out


class _EnvSettings(BaseSettings):
    """Bind LEVELSHEET__* env vars into a partial config dict."""

    model_config = SettingsConfigDict(
        env_prefix="LEVELSHEET__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    theme: dict[str, Any] | None = None
    branding: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    render: dict[str, Any] | None = None
    pivots: dict[str, Any] | None = None
    symbols: dict[str, Any] | None = None
    plugins: dict[str, Any] | None = None
    atr: dict[str, Any] | None = None
    autotrade: dict[str, Any] | None = None
    fibonacci: dict[str, Any] | None = None
    elliott_wave: dict[str, Any] | None = None
    moving_averages: dict[str, Any] | None = None
    extreme_moves: dict[str, Any] | None = None
    warnings: dict[str, Any] | None = None


def _env_overrides() -> dict[str, Any]:
    settings = _EnvSettings()
    raw = settings.model_dump(exclude_none=True)
    return raw


def load_config(cli_overrides: dict[str, Any] | None = None) -> LevelSheetConfig:
    """Load and merge configuration from all sources.

    Args:
        cli_overrides: Optional dict of CLI argparse namespace values (None values ignored).

    Returns:
        Fully validated LevelSheetConfig.
    """
    merged: dict[str, Any] = LevelSheetConfig().model_dump()
    merged = _deep_merge(merged, _load_yaml(_package_default_yaml()))
    merged = _deep_merge(merged, _load_yaml(Path.home() / ".levelsheet" / "config.yaml"))
    merged = _deep_merge(merged, _load_yaml(Path("levelsheet.yaml")))
    merged = _deep_merge(merged, _cli_to_config_dict(cli_overrides))
    merged = _deep_merge(merged, _env_overrides())
    # Also support dotenv-style single overrides already handled by pydantic-settings;
    # explicitly check LEVELSHEET__THEME__BULLISH etc. via env already.
    try:
        return LevelSheetConfig.model_validate(merged)
    except Exception as exc:  # noqa: BLE001
        raise ConfigError(f"Invalid configuration: {exc}") from exc
