"""Font registration and size scale. Implemented in Phase 3."""

from __future__ import annotations

from pathlib import Path

FONT_SIZES: dict[str, float] = {
    "header_title": 28.0,
    "header_subtitle": 14.0,
    "header_roll_warning": 11.0,
    "panel_header": 12.0,
    "table_label": 10.0,
    "table_value": 10.0,
    "bias_word": 14.0,
    "footer": 9.0,
}

DEFAULT_FONT_FAMILY = "DejaVu Sans"
MONO_FONT_FAMILY = "DejaVu Sans Mono"


def register_custom_fonts(fonts_dir: Path | None = None) -> None:
    """Register fonts from assets/fonts/ if present. Stub — Phase 3."""
    _ = fonts_dir
