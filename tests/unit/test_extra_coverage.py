"""Extra coverage for remaining edge paths."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from matplotlib.figure import Figure

from levelsheet.calc.atr import atr_wilder
from levelsheet.config.loader import load_config
from levelsheet.data.continuous_contract import build_continuous_series, list_front_contracts
from levelsheet.data.roll_calendar import (
    RollRule,
    clear_roll_rule_overrides,
    front_month_contract,
    next_roll_date,
    set_roll_rule_override,
)
from levelsheet.models.schemas import SheetData, validate_ohlc_df
from levelsheet.pipeline import build_book_bytes, generate_sheet_data
from levelsheet.render.export_pdf import export_pdf
from levelsheet.render.fonts import register_custom_fonts
from levelsheet.render.panels import daily_fib_extreme, footer
from levelsheet.render.theme import Theme


def test_atr_short_series() -> None:
    df = pd.DataFrame(
        {
            "open": [1.0, 1.1],
            "high": [1.2, 1.3],
            "low": [0.9, 1.0],
            "close": [1.1, 1.2],
        }
    )
    atr = atr_wilder(df, length=14)
    assert atr.isna().all()


def test_validate_tz_and_dupes() -> None:
    idx = pd.DatetimeIndex(["2024-01-01", "2024-01-01"]).tz_localize("UTC")
    df = pd.DataFrame(
        {
            "open": [1.0, 1.0],
            "high": [2.0, 2.0],
            "low": [0.5, 0.5],
            "close": [1.5, 1.5],
            "volume": pd.Series([1, 1], dtype="Int64"),
            "contract": ["A", "A"],
        },
        index=idx,
    )
    with pytest.raises(Exception):
        validate_ohlc_df(df)


def test_list_front_contracts() -> None:
    clear_roll_rule_overrides()
    codes = list_front_contracts("ES", date(2025, 1, 1), date(2025, 12, 31))
    assert len(codes) >= 1


def test_continuous_empty_segments(monkeypatch: pytest.MonkeyPatch) -> None:
    from levelsheet.data import continuous_contract as cc

    class P:
        name = "p"

        def is_available(self) -> bool:
            return True

        def fetch_ohlc(self, *a, **k):  # type: ignore[no-untyped-def]
            raise AssertionError("should not fetch")

    monkeypatch.setattr(cc, "_contract_sequence", lambda *a, **k: [])
    out = build_continuous_series("ES", P(), date(2024, 1, 1), date(2024, 1, 2))  # type: ignore[arg-type]
    assert out.empty


def test_daily_fib_extreme_fallback() -> None:
    fig = Figure()
    ax = fig.add_subplot(111)
    data = SheetData(
        root="ES",
        as_of_date="2026-01-01",
        extreme_moves={"+1.0%": 101.0, "-1.0%": 99.0},
        daily_fib={},
    )
    daily_fib_extreme.draw(ax, data, Theme())


def test_footer_without_logo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    fig = Figure()
    ax = fig.add_subplot(111)
    footer.draw(ax, SheetData(root="ES", as_of_date="2026-01-01", logo_path="missing.png"), Theme())


def test_register_otf(tmp_path: Path) -> None:
    (tmp_path / "x.otf").write_bytes(b"nope")
    register_custom_fonts(tmp_path)


def test_export_pdf_error(tmp_path: Path) -> None:
    from levelsheet.errors import ExportError

    fig = Figure()
    blocker = tmp_path / "file"
    blocker.write_text("x")
    with pytest.raises(ExportError):
        export_pdf(fig, blocker / "out.pdf")


def test_generate_sheet_data_and_book(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, repo_root: Path
) -> None:
    monkeypatch.chdir(repo_root)
    cfg = load_config()
    cfg.data.cache.dir = str(tmp_path / "cache")
    data = generate_sheet_data("ES", date(2026, 2, 25), cfg, pivot_method="woodie")
    assert data.daily_pivots is not None
    raw = build_book_bytes(["ES"], date(2026, 2, 25), cfg)
    assert len(raw) > 1000


def test_front_month_past_window() -> None:
    clear_roll_rule_overrides()
    set_roll_rule_override("QQ", RollRule(["H"], 0, "fixed_calendar"))
    # Far future relative to sequence end forces fallback branch
    code = front_month_contract("QQ", date(2099, 1, 1))
    assert code.startswith("QQ")
    nxt = next_roll_date("QQ", date(2099, 1, 1))
    assert isinstance(nxt, date)
    clear_roll_rule_overrides()
