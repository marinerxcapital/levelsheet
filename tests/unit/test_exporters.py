"""Unit tests for PNG/PDF exporters."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from levelsheet.config.loader import load_config
from levelsheet.render.compose import render_sheet
from levelsheet.render.export_pdf import export_book, export_pdf, sheet_to_html
from levelsheet.render.export_png import export_png
from levelsheet.render.sheet_data import build_sheet_data
from levelsheet.render.theme import Theme


def _load() -> tuple:
    daily = pd.read_csv("tests/fixtures/ES_sample.csv", parse_dates=["date"]).set_index("date")
    daily.index = pd.DatetimeIndex(daily.index).normalize()
    weekly = pd.read_csv("tests/fixtures/ES_weekly_sample.csv", parse_dates=["date"]).set_index(
        "date"
    )
    weekly.index = pd.DatetimeIndex(weekly.index).normalize()
    monthly = pd.read_csv("tests/fixtures/ES_monthly_sample.csv", parse_dates=["date"]).set_index(
        "date"
    )
    monthly.index = pd.DatetimeIndex(monthly.index).normalize()
    return daily, weekly, monthly


def test_export_png_pdf(tmp_path: Path) -> None:
    daily, weekly, monthly = _load()
    cfg = load_config()
    data = build_sheet_data("ES", daily.index[-1].date(), daily, weekly, monthly, cfg)
    theme = Theme.from_config(cfg.theme)
    fig = render_sheet(data, theme)
    png = tmp_path / "ES.png"
    pdf = tmp_path / "ES.pdf"
    export_png(fig, png)
    export_pdf(fig, pdf)
    assert png.stat().st_size > 50_000
    assert pdf.stat().st_size > 1_000


def test_export_book(tmp_path: Path) -> None:
    daily, weekly, monthly = _load()
    cfg = load_config()
    data = build_sheet_data("ES", daily.index[-1].date(), daily, weekly, monthly, cfg)
    theme = Theme.from_config(cfg.theme)
    fig = render_sheet(data, theme)
    out = tmp_path / "book.pdf"
    export_book([("ES", fig)], out)
    assert out.exists() and out.stat().st_size > 1_000


def test_sheet_to_html() -> None:
    daily, weekly, monthly = _load()
    cfg = load_config()
    data = build_sheet_data("ES", daily.index[-1].date(), daily, weekly, monthly, cfg)
    html = sheet_to_html(data, Theme.from_config(cfg.theme))
    assert "letter landscape" in html
    assert data.root in html
