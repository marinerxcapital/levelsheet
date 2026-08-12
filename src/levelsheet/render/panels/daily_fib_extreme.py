"""Daily fibonacci + extreme moves panel."""

from __future__ import annotations

from matplotlib.axes import Axes

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES, MONO_FONT_FAMILY
from levelsheet.render.panels._shared import draw_fib_table, format_price
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw daily fib table; extreme moves listed beneath via extras if crowded."""
    levels = data.daily_fib or data.extreme_moves or {"0.0%": 0.0}
    # Prefer daily fib; append extreme moves into a combined view when daily fib empty
    if data.daily_fib:
        draw_fib_table(ax, data.daily_fib, theme, "Daily Fib", decimals=data.decimals)
    else:
        ax.axis("off")
        ax.text(
            0.5,
            0.98,
            "EXTREME MOVES",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=FONT_SIZES["panel_header"],
            fontweight="bold",
            color=theme.body_text,
            fontfamily=theme.font_family,
        )
        items = list(levels.items())
        for i, (lab, val) in enumerate(items):
            y = 0.90 - i * (0.85 / max(len(items), 1))
            color = (
                theme.bullish
                if lab.startswith("+")
                else (theme.bearish if lab.startswith("-") else theme.body_text)
            )
            ax.text(
                0.08,
                y,
                lab,
                transform=ax.transAxes,
                ha="left",
                va="center",
                fontsize=FONT_SIZES["table_label"],
                color=color,
                fontfamily=theme.font_family,
            )
            ax.text(
                0.92,
                y,
                format_price(val, data.decimals),
                transform=ax.transAxes,
                ha="right",
                va="center",
                fontsize=FONT_SIZES["table_value"],
                color=color,
                fontfamily=MONO_FONT_FAMILY,
            )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Daily Fib / Extreme</div>"
