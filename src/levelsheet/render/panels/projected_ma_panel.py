"""Projected MA panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw MA length / today / projected tomorrow table."""
    ax.axis("off")
    ax.text(
        0.5, 0.98, "PROJECTED MA", transform=ax.transAxes, ha="center", va="top",
        fontsize=FONT_SIZES["panel_header"], fontweight="bold",
        color=theme.body_text, fontfamily=theme.font_family,
    )
    items = list(data.projected_mas.items())[:6]
    if not items:
        items = [(5, (0.0, 0.0))]
    # header
    ax.text(0.05, 0.88, "Len", transform=ax.transAxes, fontsize=8, color=theme.neutral,
            fontfamily=theme.font_family)
    ax.text(0.35, 0.88, "Today", transform=ax.transAxes, fontsize=8, color=theme.neutral,
            fontfamily=theme.font_family)
    ax.text(0.70, 0.88, "Proj", transform=ax.transAxes, fontsize=8, color=theme.neutral,
            fontfamily=theme.font_family)
    for i, (length, (today, proj)) in enumerate(items):
        y = 0.75 - i * 0.12
        ax.text(0.05, y, str(length), transform=ax.transAxes, ha="left", va="center",
                fontsize=FONT_SIZES["table_label"], color=theme.body_text,
                fontfamily=theme.font_family)
        ax.text(0.35, y, format_price(today, data.decimals), transform=ax.transAxes,
                ha="left", va="center", fontsize=FONT_SIZES["table_value"],
                color=theme.body_text, fontfamily=MONO_FONT_FAMILY)
        ax.add_patch(
            Rectangle(
                (0.65, y - 0.04), 0.33, 0.09, transform=ax.transAxes,
                facecolor=theme.open_settlement, edgecolor=theme.border,
                linewidth=theme.border_width_pt, clip_on=False,
            )
        )
        ax.text(0.70, y, format_price(proj, data.decimals), transform=ax.transAxes,
                ha="left", va="center", fontsize=FONT_SIZES["table_value"],
                color=theme.body_text, fontfamily=MONO_FONT_FAMILY)


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Projected MA</div>"
