"""Weekly and monthly pivot panels."""

from __future__ import annotations

from matplotlib.axes import Axes

from levelsheet.calc.pivots import PivotSet
from levelsheet.models.schemas import SheetData
from levelsheet.render.panels._shared import draw_pivot_table
from levelsheet.render.theme import Theme


def draw_weekly(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw weekly pivot table."""
    pivots = data.weekly_pivots or PivotSet(p=0, r1=0, r2=0, s1=0, s2=0)
    draw_pivot_table(ax, pivots, theme, "Weekly", decimals=data.decimals)


def draw_monthly(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw monthly pivot table."""
    pivots = data.monthly_pivots or PivotSet(p=0, r1=0, r2=0, s1=0, s2=0)
    draw_pivot_table(ax, pivots, theme, "Monthly", decimals=data.decimals)


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Default draw — weekly (caller selects weekly/monthly via dedicated funcs)."""
    draw_weekly(ax, data, theme)


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Weekly/Monthly pivots</div>"
