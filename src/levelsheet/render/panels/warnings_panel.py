"""Warnings panel."""

from __future__ import annotations

from matplotlib.axes import Axes

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES
from levelsheet.render.panels._shared import draw_pill
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw stacked warning pills."""
    ax.axis("off")
    ax.text(
        0.5,
        0.98,
        "WARNINGS",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    flags = [
        ("FALSE DAY", data.warnings.get("false_day", False)),
        ("RTH GAP", data.warnings.get("rth_gap", False)),
        ("BLUD / AHDD", data.warnings.get("blud", False) or data.warnings.get("ahdd", False)),
    ]
    for i, (lab, flagged) in enumerate(flags):
        y = 0.70 - i * 0.25
        draw_pill(
            ax,
            0.05,
            y,
            0.90,
            0.18,
            lab,
            theme.bearish if flagged else theme.neutral,
            "#FFFFFF" if flagged else theme.neutral,
            theme,
            fontsize=11,
            outline_only=not flagged,
        )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return f"<div>Warnings: {data.warnings}</div>"
