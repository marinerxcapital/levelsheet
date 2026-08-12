"""mini_candlestick panel renderer. Stub — Phase 3."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from levelsheet.models.schemas import SheetData
    from levelsheet.render.theme import Theme


def draw(ax: "Axes", data: "SheetData", theme: "Theme") -> None:
    """Draw the mini_candlestick panel. Stub — Phase 3."""
    raise NotImplementedError("Phase 3")


def to_html(data: "SheetData", theme: "Theme") -> str:
    """HTML fragment for weasyprint fallback. Stub — Phase 4."""
    raise NotImplementedError("Phase 4")
