"""Auto-trade settings panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw 8-row autotrade label/value table."""
    ax.axis("off")
    ax.add_patch(
        Rectangle(
            (0, 0.85),
            1,
            0.15,
            transform=ax.transAxes,
            facecolor=theme.header_bg,
            edgecolor=theme.border,
            linewidth=theme.border_width_pt,
            clip_on=False,
        )
    )
    ax.text(
        0.5,
        0.925,
        "AUTOTRADE",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.header_text,
        fontfamily=theme.font_family,
    )
    at = data.autotrade
    rows = [
        ("Max Stop", format_price(at.max_stop, data.decimals) if at else "n/a"),
        ("Trail", format_price(at.trail, data.decimals) if at else "n/a"),
        ("Frequency", at.frequency if at else "n/a"),
        ("Max Target", format_price(at.max_target, data.decimals) if at else "n/a"),
        ("Side", at.side if at else "n/a"),
        ("Size", str(at.size) if at else "n/a"),
        ("Scale Out %", f"{at.scale_out:.1f}" if at else "n/a"),
        ("Max Risk $", format_price(at.max_risk_dollars, 2) if at else "n/a"),
    ]
    for i, (lab, val) in enumerate(rows):
        y = 0.80 - i * 0.10
        ax.text(
            0.05,
            y,
            lab,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=8,
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        ax.text(
            0.95,
            y,
            val,
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=8,
            color=theme.body_text,
            fontfamily=MONO_FONT_FAMILY,
        )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Autotrade</div>"
