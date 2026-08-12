"""Header panel renderer."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw header with title, subtitle, and roll warning."""
    ax.axis("off")
    ax.add_patch(
        Rectangle(
            (0, 0),
            1,
            1,
            transform=ax.transAxes,
            facecolor=theme.header_bg,
            edgecolor="none",
            clip_on=False,
        )
    )
    ax.text(
        0.01,
        0.85,
        f"{data.company_name}  —  {data.root} DAILY LEVELS",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_SIZES["header_title"],
        fontweight="bold",
        color=theme.header_text,
        fontfamily=theme.font_family,
    )
    ax.text(
        0.01,
        0.50,
        f"Contract {data.contract}  |  As of {data.as_of_date}",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=FONT_SIZES["header_subtitle"],
        color=theme.header_text,
        fontfamily=theme.font_family,
    )
    roll_color = theme.bearish if data.days_to_roll <= 5 else theme.neutral
    # On dark header bg, use light text unless urgent (bearish stays red)
    text_color = roll_color if data.days_to_roll <= 5 else theme.header_text
    ax.text(
        0.01,
        0.15,
        f"Days to roll: {data.days_to_roll}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=FONT_SIZES["header_roll_warning"],
        fontstyle="italic",
        color=text_color,
        fontfamily=theme.font_family,
    )


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return (
        f'<div style="background:{theme.header_bg};color:{theme.header_text};padding:8px;">'
        f"<strong>{data.company_name} — {data.root}</strong> "
        f"{data.as_of_date} | roll {data.days_to_roll}d</div>"
    )
