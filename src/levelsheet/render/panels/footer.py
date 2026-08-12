"""Footer panel."""

from __future__ import annotations

from pathlib import Path

from matplotlib.axes import Axes

from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES
from levelsheet.render.theme import Theme


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw centered footer text; composite logo if present."""
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        data.footer_text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=FONT_SIZES["footer"],
        color=theme.footer_text,
        fontfamily=theme.font_family,
    )
    logo = Path(data.logo_path) if data.logo_path else Path("assets/logo/logo.png")
    if logo.exists():
        try:
            import matplotlib.pyplot as plt
            from matplotlib.offsetbox import AnnotationBbox, OffsetImage

            img = plt.imread(str(logo))
            imagebox = OffsetImage(img, zoom=0.15)
            ab = AnnotationBbox(imagebox, (0.95, 0.5), xycoords=ax.transAxes, frameon=False)
            ax.add_artist(ab)
        except Exception:  # noqa: BLE001
            pass


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return f'<div style="color:{theme.footer_text};text-align:center;">{data.footer_text}</div>'
