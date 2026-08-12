"""Elliott wave panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw Wave 0–5 table + projection pill."""
    ax.axis("off")
    ax.text(
        0.5, 0.98, "ELLIOTT WAVE", transform=ax.transAxes, ha="center", va="top",
        fontsize=FONT_SIZES["panel_header"], fontweight="bold",
        color=theme.body_text, fontfamily=theme.font_family,
    )
    waves = data.elliott.waves if data.elliott else []
    for i in range(6):
        y = 0.85 - i * 0.10
        if i < len(waves):
            w = waves[i]
            label = f"Wave {i}: {w.get('kind', '')} @ {format_price(float(w.get('price', 0)), data.decimals)}"
        else:
            label = f"Wave {i}: —"
        ax.text(0.05, y, label, transform=ax.transAxes, ha="left", va="center",
                fontsize=FONT_SIZES["table_label"], color=theme.body_text,
                fontfamily=theme.font_family)
    target = data.elliott.wave5_target if data.elliott else 0.0
    ratio = data.elliott.ext_ratio if data.elliott else 0.0
    ax.add_patch(
        FancyBboxPatch(
            (0.05, 0.02), 0.90, 0.12, boxstyle="round,pad=0.02",
            transform=ax.transAxes, facecolor=theme.key_level,
            edgecolor=theme.border, linewidth=theme.border_width_pt, clip_on=False,
        )
    )
    ax.text(
        0.5, 0.08,
        f"Wave5 target {format_price(target, data.decimals)} (ext {ratio})",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=9, color=theme.key_level_text, fontfamily=MONO_FONT_FAMILY,
    )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Elliott</div>"
