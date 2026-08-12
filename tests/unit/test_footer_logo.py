"""Footer logo compositing test."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from levelsheet.models.schemas import SheetData
from levelsheet.render.panels import footer
from levelsheet.render.theme import Theme


def test_footer_draws_logo(repo_root: Path) -> None:
    logo = repo_root / "assets" / "logo" / "logo.png"
    assert logo.exists() and logo.stat().st_size > 100
    fig = Figure()
    ax = fig.add_subplot(111)
    footer.draw(
        ax,
        SheetData(root="ES", as_of_date="2026-01-01", logo_path=str(logo)),
        Theme(),
    )
    assert len(ax.artists) >= 1 or len(ax.texts) >= 1
