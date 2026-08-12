"""End-to-end sheet generation pipeline."""

from __future__ import annotations

import io
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from matplotlib.figure import Figure

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.cache import CachedDataFetcher
from levelsheet.data.providers import get_provider_chain
from levelsheet.data.roll_calendar import RollRule, set_roll_rule_override
from levelsheet.models.schemas import SheetData
from levelsheet.render.compose import render_sheet
from levelsheet.render.export_pdf import (
    export_book,
    export_pdf,
    export_pdf_weasyprint,
    sheet_to_html,
)
from levelsheet.render.export_png import export_png
from levelsheet.render.sheet_data import build_sheet_data
from levelsheet.render.theme import Theme


def _parse_date(value: Optional[str]) -> date:
    if value is None:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_fixture_frames(root: str = "ES") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load committed CSV fixtures (used when network providers fail in tests/dev)."""
    candidates = [
        Path("tests/fixtures"),
        Path(__file__).resolve().parents[2] / "tests" / "fixtures",
    ]
    base = next((p for p in candidates if (p / f"{root}_sample.csv").exists()), candidates[0])
    daily = pd.read_csv(base / f"{root}_sample.csv", parse_dates=["date"]).set_index("date")
    weekly = pd.read_csv(base / f"{root}_weekly_sample.csv", parse_dates=["date"]).set_index("date")
    monthly = pd.read_csv(base / f"{root}_monthly_sample.csv", parse_dates=["date"]).set_index(
        "date"
    )
    for df in (daily, weekly, monthly):
        df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
        if "volume" in df.columns:
            df["volume"] = df["volume"].astype("Int64")
    return daily, weekly, monthly


def fetch_frames(
    root: str,
    as_of: date,
    config: LevelSheetConfig,
    force_refresh: bool = False,
    allow_fixtures: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch daily/weekly/monthly frames via cache+providers, with fixture fallback."""
    providers = get_provider_chain(config)
    fetcher = CachedDataFetcher(providers, config)
    start = as_of - timedelta(days=365 * 3)
    try:
        daily = fetcher.fetch(
            root, "1d", start, as_of, as_of_date=as_of, force_refresh=force_refresh
        )
        weekly = fetcher.fetch(
            root, "1wk", start, as_of, as_of_date=as_of, force_refresh=force_refresh
        )
        monthly = fetcher.fetch(
            root, "1mo", start, as_of, as_of_date=as_of, force_refresh=force_refresh
        )
        # Slice to as_of
        daily = daily.loc[daily.index.date <= as_of]  # type: ignore[attr-defined]
        return daily, weekly, monthly
    except Exception as exc:  # noqa: BLE001
        logger.warning("Provider fetch failed for {}: {}; trying fixtures", root, exc)
        if allow_fixtures and root.upper() == "ES":
            return load_fixture_frames("ES")
        raise


def generate_sheet_data(
    root: str,
    as_of: date,
    config: LevelSheetConfig,
    force_refresh: bool = False,
    pivot_method: Optional[str] = None,
) -> SheetData:
    """Fetch data and build SheetData."""
    if pivot_method:
        config = config.model_copy(deep=True)
        config.pivots.method = pivot_method  # type: ignore[assignment]
    daily, weekly, monthly = fetch_frames(root, as_of, config, force_refresh=force_refresh)
    return build_sheet_data(root, as_of, daily, weekly, monthly, config)


def generate_figure(
    root: str,
    as_of: date,
    config: LevelSheetConfig,
    force_refresh: bool = False,
    pivot_method: Optional[str] = None,
) -> tuple[SheetData, Figure]:
    """Build SheetData and render figure."""
    data = generate_sheet_data(root, as_of, config, force_refresh, pivot_method)
    theme = Theme.from_config(config.theme)
    fig = render_sheet(data, theme)
    return data, fig


def export_sheet_files(
    root: str,
    as_of: date,
    config: LevelSheetConfig,
    output_dir: Path,
    formats: list[str],
    force_refresh: bool = False,
) -> dict[str, Path]:
    """Generate and write PDF/PNG outputs; return path map."""
    data, fig = generate_figure(root, as_of, config, force_refresh=force_refresh)
    output_dir = Path(output_dir)
    results: dict[str, Path] = {}
    stem = f"{root.upper()}_{as_of.isoformat()}"
    if config.render.engine == "weasyprint" and "pdf" in formats:
        html = sheet_to_html(data, Theme.from_config(config.theme))
        pdf_path = output_dir / "pdf" / f"{stem}.pdf"
        export_pdf_weasyprint(html, pdf_path)
        results["pdf"] = pdf_path
    else:
        if "pdf" in formats:
            pdf_path = output_dir / "pdf" / f"{stem}.pdf"
            export_pdf(fig, pdf_path)
            results["pdf"] = pdf_path
    if "png" in formats:
        png_path = output_dir / "png" / f"{stem}.png"
        export_png(fig, png_path)
        results["png"] = png_path
    return results


def build_sheet_bytes(
    root: str,
    as_of: date,
    config: LevelSheetConfig,
    pivot_method: str = "classic",
) -> tuple[Figure, bytes, bytes]:
    """Return (fig, pdf_bytes, png_bytes) for Streamlit downloads."""
    data, fig = generate_figure(root, as_of, config, pivot_method=pivot_method)
    pdf_buf = io.BytesIO()
    png_buf = io.BytesIO()
    fig.set_size_inches(17, 11)
    fig.savefig(pdf_buf, format="pdf")
    fig.savefig(png_buf, format="png", dpi=300, facecolor=fig.get_facecolor())
    return fig, pdf_buf.getvalue(), png_buf.getvalue()


def build_book_bytes(roots: list[str], as_of: date, config: LevelSheetConfig) -> bytes:
    """Build multi-page book PDF bytes."""
    sheets: list[tuple[str, Figure]] = []
    for root in roots:
        _, fig = generate_figure(root, as_of, config)
        sheets.append((root, fig))
    buf_path = Path("/tmp") / f"levelsheet_book_{as_of.isoformat()}.pdf"
    export_book(sheets, buf_path)
    return buf_path.read_bytes()


def apply_roll_rule_json(root: str, raw: str) -> None:
    """Parse and register a RollRule override from JSON."""
    import json

    payload = json.loads(raw)
    rule = RollRule(
        contract_months=list(payload["contract_months"]),
        days_before_first_notice=int(payload["days_before_first_notice"]),
        roll_reference=payload["roll_reference"],
    )
    set_roll_rule_override(root, rule)


# Re-export helpers used by CLI
parse_date = _parse_date
