"""Bias panel — 2×3 grid of MA lookback bias cells."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES
from levelsheet.render.panels._shared import bias_colors
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw 2×3 bias grid for configured MA lengths."""
    ax.axis("off")
    ax.text(
        0.5,
        0.98,
        "BIAS",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    lengths = sorted(data.ma_bias.keys()) or [5, 13, 50, 100, 150, 200]
    lengths = lengths[:6]
    while len(lengths) < 6:
        lengths.append(lengths[-1] if lengths else 5)
    for i, length in enumerate(lengths):
        col = i % 3
        row = i // 3
        x = 0.03 + col * 0.32
        y = 0.52 - row * 0.45
        w, h = 0.30, 0.40
        b = data.ma_bias.get(length, "NONE")
        fill, text_c = bias_colors(b, theme)
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02",
                transform=ax.transAxes,
                facecolor=fill,
                edgecolor=theme.border,
                linewidth=theme.border_width_pt,
                clip_on=False,
            )
        )
        ax.text(
            x + w / 2,
            y + h * 0.70,
            f"MA{length}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        ax.text(
            x + w / 2,
            y + h * 0.30,
            b,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=FONT_SIZES["bias_word"],
            fontweight="bold",
            color=text_c,
            fontfamily=theme.font_family,
        )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return f"<div>Bias: {data.ma_bias}</div>"
