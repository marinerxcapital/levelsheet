"""Color theme dataclass. Fully wired in Phase 3/6."""

from __future__ import annotations

from dataclasses import dataclass

from levelsheet.config.schema import ThemeConfig


@dataclass(frozen=True)
class Theme:
    """Renderable color theme."""

    bullish: str = "#1B7A3D"
    bullish_fill_light: str = "#E9F6EC"
    bearish: str = "#B32020"
    bearish_fill_light: str = "#FBE9E9"
    key_level: str = "#F2C230"
    key_level_text: str = "#5A4300"
    open_settlement: str = "#ADD8E6"
    neutral: str = "#8C8C8C"
    header_bg: str = "#0B1F33"
    header_text: str = "#FFFFFF"
    border: str = "#333333"
    border_width_pt: float = 0.75
    body_text: str = "#1A1A1A"
    footer_text: str = "#777777"
    font_family: str = "DejaVu Sans"

    @classmethod
    def from_config(cls, cfg: ThemeConfig) -> "Theme":
        """Build Theme from pydantic ThemeConfig."""
        return cls(
            bullish=cfg.bullish,
            bullish_fill_light=cfg.bullish_fill_light,
            bearish=cfg.bearish,
            bearish_fill_light=cfg.bearish_fill_light,
            key_level=cfg.key_level,
            key_level_text=cfg.key_level_text,
            open_settlement=cfg.open_settlement,
            neutral=cfg.neutral,
            header_bg=cfg.header_bg,
            header_text=cfg.header_text,
            border=cfg.border,
            font_family=cfg.font_family,
        )
