"""Daily pivots panel renderer."""

from __future__ import annotations

from matplotlib.axes import Axes

from levelsheet.calc.pivots import PivotSet
from levelsheet.models.schemas import SheetData
from levelsheet.render.panels._shared import draw_pivot_table
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw daily classic pivot table."""
    pivots = data.daily_pivots or PivotSet(p=0, r1=0, r2=0, s1=0, s2=0)
    draw_pivot_table(ax, pivots, theme, "Daily Pivots", decimals=data.decimals)


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    p = data.daily_pivots
    if p is None:
        return "<div>Daily Pivots: n/a</div>"
    return f"<div><b>Daily Pivots</b> P={p.p} R1={p.r1} S1={p.s1}</div>"
