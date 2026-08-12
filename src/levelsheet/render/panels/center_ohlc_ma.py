"""Center OHLC + MA bias panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import bias_colors, format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw OHLC/GSO grid (top) and MA bias table (bottom)."""
    ax.axis("off")
    bar = data.today_bar
    decimals = data.decimals

    # Top half: OHLC
    ax.text(
        0.5,
        0.98,
        "OHLC / SESSION",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    labels = ["Open", "High", "Low", "Close", "Range", "Mid"]
    if bar is not None:
        rng = bar.high - bar.low
        mid = (bar.high + bar.low) / 2
        values = [bar.open, bar.high, bar.low, bar.close, rng, mid]
    else:
        values = [0.0] * 6
    for i, (lab, val) in enumerate(zip(labels, values)):
        y = 0.90 - i * 0.055
        ax.text(
            0.08,
            y,
            lab,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=FONT_SIZES["table_label"],
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        ax.text(
            0.92,
            y,
            format_price(val, decimals),
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=FONT_SIZES["table_value"],
            color=theme.body_text,
            fontfamily=MONO_FONT_FAMILY,
        )

    # Bottom half: MA table
    ax.text(
        0.5,
        0.52,
        "MOVING AVERAGES",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    lengths = sorted(data.ma_values.keys()) or [5, 13, 50, 100, 150, 200]
    for i, length in enumerate(lengths):
        y = 0.45 - i * 0.07
        val = data.ma_values.get(length, float("nan"))
        b = data.ma_bias.get(length, "NONE")
        fill, text_c = bias_colors(b, theme)
        ax.text(
            0.05,
            y + 0.02,
            f"MA{length}",
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=FONT_SIZES["table_label"],
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        ax.text(
            0.45,
            y + 0.02,
            format_price(val, decimals) if val == val else "n/a",
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=FONT_SIZES["table_value"],
            color=theme.body_text,
            fontfamily=MONO_FONT_FAMILY,
        )
        ax.add_patch(
            FancyBboxPatch(
                (0.72, y - 0.01),
                0.25,
                0.055,
                boxstyle="round,pad=0.02",
                transform=ax.transAxes,
                facecolor=fill,
                edgecolor=theme.border,
                linewidth=theme.border_width_pt,
                clip_on=False,
            )
        )
        ax.text(
            0.845,
            y + 0.02,
            b,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=text_c,
            fontfamily=theme.font_family,
        )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return f"<div>OHLC/MA panel for {data.root}</div>"
