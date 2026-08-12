"""Font registration and size scale."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

FONT_SIZES: dict[str, float] = {
    "header_title": 28.0,
    "header_subtitle": 14.0,
    "header_roll_warning": 11.0,
    "panel_header": 12.0,
    "table_label": 10.0,
    "table_value": 10.0,
    "bias_word": 14.0,
    "footer": 9.0,
    "stat_large": 18.0,
}

DEFAULT_FONT_FAMILY = "DejaVu Sans"
MONO_FONT_FAMILY = "DejaVu Sans Mono"


def register_custom_fonts(fonts_dir: Path | None = None) -> None:
    """Register fonts from assets/fonts/ if present."""
    from matplotlib import font_manager

    directory = fonts_dir or Path("assets/fonts")
    if not directory.exists():
        return
    for path in directory.glob("*.ttf"):
        try:
            font_manager.fontManager.addfont(str(path))
            logger.debug("Registered font {}", path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to register font {}: {}", path, exc)
    for path in directory.glob("*.otf"):
        try:
            font_manager.fontManager.addfont(str(path))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to register font {}: {}", path, exc)
