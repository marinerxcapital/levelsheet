"""PDF and multi-page book export (matplotlib + weasyprint). Stub — Phase 4."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure


def export_pdf(fig: Figure, path: Path) -> None:
    """Save figure as US-Letter-landscape PDF. Stub — Phase 4."""
    raise NotImplementedError("Phase 4")


def export_book(sheets: list[tuple[str, Figure]], path: Path) -> None:
    """Concatenate multiple sheets into one multi-page PDF. Stub — Phase 4."""
    raise NotImplementedError("Phase 4")


def export_pdf_weasyprint(html: str, path: Path) -> None:
    """HTML→PDF via weasyprint. Stub — Phase 4."""
    raise NotImplementedError("Phase 4")
