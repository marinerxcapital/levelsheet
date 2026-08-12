"""ATR / NR7 / WR7 / hi-lo panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import draw_pill, format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw ATR stat box, NR7/WR7 badges, and 7/20 hi-lo grid."""
    ax.axis("off")
    ax.text(
        0.5,
        0.98,
        "ATR / NR7",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    ax.add_patch(
        Rectangle(
            (0.05, 0.55),
            0.90,
            0.35,
            transform=ax.transAxes,
            facecolor=theme.open_settlement,
            edgecolor=theme.border,
            linewidth=theme.border_width_pt,
            clip_on=False,
        )
    )
    atr = data.atr_5d if data.atr_5d is not None else data.atr_value
    ax.text(
        0.5,
        0.72,
        format_price(atr or 0.0, data.decimals),
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=FONT_SIZES["stat_large"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=MONO_FONT_FAMILY,
    )
    ax.text(
        0.5,
        0.58,
        "5-D ATR",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9,
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    draw_pill(
        ax, 0.05, 0.35, 0.42, 0.15, "NR7",
        theme.bullish if data.nr7 else theme.neutral,
        "#FFFFFF" if data.nr7 else theme.neutral,
        theme,
        outline_only=not data.nr7,
    )
    draw_pill(
        ax, 0.53, 0.35, 0.42, 0.15, "WR7",
        theme.bullish if data.wr7 else theme.neutral,
        "#FFFFFF" if data.wr7 else theme.neutral,
        theme,
        outline_only=not data.wr7,
    )
    # 7/20 hi-lo compact grid
    grid = [
        ("7H", data.hi_7),
        ("7L", data.lo_7),
        ("20H", data.hi_20),
        ("20L", data.lo_20),
    ]
    for i, (lab, val) in enumerate(grid):
        col = i % 2
        row = i // 2
        x = 0.05 + col * 0.48
        y = 0.18 - row * 0.16
        ax.text(x, y, f"{lab}: {format_price(val or 0.0, data.decimals)}",
                transform=ax.transAxes, ha="left", va="center",
                fontsize=8, color=theme.body_text, fontfamily=theme.font_family)


def draw_hilo(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Dedicated 7/20 hi-lo panel for layout slot hilo_7_20_panel."""
    ax.axis("off")
    ax.text(
        0.5, 0.98, "7 / 20 HI-LO", transform=ax.transAxes, ha="center", va="top",
        fontsize=FONT_SIZES["panel_header"], fontweight="bold",
        color=theme.body_text, fontfamily=theme.font_family,
    )
    items = [
        ("7-Day High", data.hi_7),
        ("7-Day Low", data.lo_7),
        ("20-Day High", data.hi_20),
        ("20-Day Low", data.lo_20),
    ]
    for i, (lab, val) in enumerate(items):
        y = 0.75 - i * 0.18
        ax.add_patch(
            Rectangle(
                (0.0, y - 0.05), 1.0, 0.15, transform=ax.transAxes,
                facecolor=theme.open_settlement if i % 2 == 0 else "#FFFFFF",
                edgecolor=theme.border, linewidth=theme.border_width_pt, clip_on=False,
            )
        )
        ax.text(0.08, y + 0.025, lab, transform=ax.transAxes, ha="left", va="center",
                fontsize=FONT_SIZES["table_label"], color=theme.body_text,
                fontfamily=theme.font_family)
        ax.text(0.92, y + 0.025, format_price(val or 0.0, data.decimals),
                transform=ax.transAxes, ha="right", va="center",
                fontsize=FONT_SIZES["table_value"], color=theme.body_text,
                fontfamily=MONO_FONT_FAMILY)


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return f"<div>ATR={data.atr_value} NR7={data.nr7} WR7={data.wr7}</div>"
