"""PDF and multi-page book export (matplotlib + weasyprint)."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from levelsheet.errors import ExportError
from levelsheet.models.schemas import SheetData
from levelsheet.render.theme import Theme


def export_pdf(fig: Figure, path: Path) -> None:
    """Save figure as US-Letter-landscape PDF."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.set_size_inches(17, 11)
        fig.savefig(path, format="pdf")
    except Exception as exc:  # noqa: BLE001
        raise ExportError(f"Failed to write PDF {path}") from exc
    if not path.exists() or path.stat().st_size <= 1_000:
        raise ExportError(f"PDF sanity check failed for {path}")


def export_book(sheets: list[tuple[str, Figure]], path: Path) -> None:
    """Concatenate multiple sheets into one multi-page PDF."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with PdfPages(path) as pdf:
            for _name, fig in sheets:
                fig.set_size_inches(17, 11)
                pdf.savefig(fig)
    except Exception as exc:  # noqa: BLE001
        raise ExportError(f"Failed to write book PDF {path}") from exc


def build_full_html(fragments: list[str], theme: Theme) -> str:
    """Wrap panel HTML fragments in a letter-landscape page."""
    body = "\n".join(fragments)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
@page {{ size: letter landscape; margin: 0.4in; }}
body {{ font-family: '{theme.font_family}', sans-serif; color: {theme.body_text}; }}
</style></head><body>{body}</body></html>"""


def export_pdf_weasyprint(html: str, path: Path) -> None:
    """HTML→PDF via weasyprint."""
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise ExportError("weasyprint not installed") from exc
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html).write_pdf(path)
    except Exception as exc:  # noqa: BLE001
        raise ExportError(f"weasyprint failed for {path}") from exc


def sheet_to_html(data: SheetData, theme: Theme) -> str:
    """Assemble full HTML page from all panel to_html fragments."""
    from levelsheet.render.panels import (
        atr_nr7,
        autotrade_panel,
        bias_panel,
        center_ohlc_ma,
        daily_fib_extreme,
        daily_pivots,
        elliott_panel,
        footer,
        header,
        long_term_fib,
        mini_candlestick,
        projected_ma_panel,
        warnings_panel,
        weekly_monthly,
    )

    fragments = [
        header.to_html(data, theme),
        daily_pivots.to_html(data, theme),
        center_ohlc_ma.to_html(data, theme),
        mini_candlestick.to_html(data, theme),
        weekly_monthly.to_html(data, theme),
        atr_nr7.to_html(data, theme),
        long_term_fib.to_html(data, theme),
        daily_fib_extreme.to_html(data, theme),
        bias_panel.to_html(data, theme),
        autotrade_panel.to_html(data, theme),
        elliott_panel.to_html(data, theme),
        projected_ma_panel.to_html(data, theme),
        warnings_panel.to_html(data, theme),
        footer.to_html(data, theme),
    ]
    return build_full_html(fragments, theme)
