"""Long-term Fibonacci panel."""

from __future__ import annotations

from matplotlib.axes import Axes

from levelsheet.models.schemas import SheetData
from levelsheet.render.panels._shared import draw_fib_table
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw long-term fibonacci levels."""
    draw_fib_table(
        ax, data.long_term_fib or {"0.0%": 0.0}, theme, "Long-Term Fib", decimals=data.decimals
    )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Long-term Fib</div>"
