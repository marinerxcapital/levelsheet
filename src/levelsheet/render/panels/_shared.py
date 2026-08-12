"""Shared panel drawing helpers."""

from __future__ import annotations

from typing import Optional

from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch, Rectangle

from levelsheet.calc.pivots import PivotSet
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.theme import Theme


def format_price(value: float, decimals: int = 2) -> str:
    """Format numeric price with thousands separator."""
    if decimals == 4:
        return f"{value:,.4f}"
    return f"{value:,.2f}"


def draw_pivot_table(
    ax: Axes,
    pivot_set: PivotSet,
    theme: Theme,
    header_label: str,
    decimals: int = 2,
) -> None:
    """Draw stacked R/P/S pivot rows with theme fills."""
    ax.axis("off")
    rows: list[tuple[str, Optional[float], str]] = []
    for label, attr, kind in [
        ("R3", "r3", "R"),
        ("R2", "r2", "R"),
        ("R1", "r1", "R"),
        ("PIVOT", "p", "P"),
        ("S1", "s1", "S"),
        ("S2", "s2", "S"),
        ("S3", "s3", "S"),
    ]:
        val = getattr(pivot_set, attr, None)
        if val is not None:
            rows.append((label, float(val), kind))
    n = max(len(rows), 1)
    # Header
    ax.text(
        0.5,
        0.98,
        header_label.upper(),
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    top = 0.90
    height = 0.90 / n
    for i, (label, val, kind) in enumerate(rows):
        y = top - (i + 1) * height
        if kind == "R":
            fill, text_c = theme.bullish_fill_light, theme.bullish
        elif kind == "S":
            fill, text_c = theme.bearish_fill_light, theme.bearish
        else:
            fill, text_c = theme.key_level, theme.key_level_text
        ax.add_patch(
            Rectangle(
                (0.0, y),
                1.0,
                height,
                transform=ax.transAxes,
                facecolor=fill,
                edgecolor=theme.border,
                linewidth=theme.border_width_pt,
                clip_on=False,
            )
        )
        ax.text(
            0.08,
            y + height / 2,
            label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=FONT_SIZES["table_label"],
            color=text_c,
            fontfamily=theme.font_family,
        )
        ax.text(
            0.92,
            y + height / 2,
            format_price(val or 0.0, decimals),
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=FONT_SIZES["table_value"],
            color=text_c,
            fontfamily=MONO_FONT_FAMILY,
        )


def draw_fib_table(
    ax: Axes,
    levels: dict[str, float],
    theme: Theme,
    header_label: str,
    key_levels: set[str] | None = None,
    decimals: int = 2,
) -> None:
    """Draw fibonacci level table; highlight key rows."""
    ax.axis("off")
    key_levels = key_levels or {"61.8%", "50.0%", "38.2%"}
    ax.text(
        0.5,
        0.98,
        header_label.upper(),
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    items = list(levels.items())
    n = max(len(items), 1)
    top = 0.90
    height = 0.90 / n
    for i, (label, val) in enumerate(items):
        y = top - (i + 1) * height
        is_key = label in key_levels
        fill = theme.key_level if is_key else "#FFFFFF"
        alpha = 0.25 if is_key else 1.0
        ax.add_patch(
            Rectangle(
                (0.0, y),
                1.0,
                height,
                transform=ax.transAxes,
                facecolor=fill,
                edgecolor=theme.border,
                linewidth=theme.border_width_pt,
                alpha=alpha if is_key else 1.0,
                clip_on=False,
            )
        )
        ax.text(
            0.08,
            y + height / 2,
            label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=FONT_SIZES["table_label"],
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        ax.text(
            0.92,
            y + height / 2,
            format_price(val, decimals),
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=FONT_SIZES["table_value"],
            color=theme.body_text,
            fontfamily=MONO_FONT_FAMILY,
        )


def bias_colors(bias_word: str, theme: Theme) -> tuple[str, str]:
    """Return (fill, text) colors for a bias word."""
    if bias_word == "LONG":
        return theme.bullish_fill_light, theme.bullish
    if bias_word == "SHORT":
        return theme.bearish_fill_light, theme.bearish
    return "#FFFFFF", theme.neutral


def draw_pill(
    ax: Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    fill: str,
    text_color: str,
    theme: Theme,
    fontsize: float = 10.0,
    outline_only: bool = False,
) -> None:
    """Draw a rounded pill badge."""
    facecolor = "none" if outline_only else fill
    edge = theme.neutral if outline_only else theme.border
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02",
            transform=ax.transAxes,
            facecolor=facecolor,
            edgecolor=edge,
            linewidth=theme.border_width_pt,
            clip_on=False,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=text_color,
        fontfamily=theme.font_family,
        fontweight="bold",
    )
