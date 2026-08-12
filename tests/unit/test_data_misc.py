"""Unit tests for symbols, roll calendar, schemas, providers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from matplotlib.figure import Figure

from levelsheet.config.loader import load_config
from levelsheet.data.providers import get_provider_chain
from levelsheet.data.providers.ib_provider import IBProvider
from levelsheet.data.providers.polygon_provider import PolygonProvider
from levelsheet.data.providers.yfinance_provider import YFinanceProvider
from levelsheet.data.roll_calendar import (
    RollRule,
    clear_roll_rule_overrides,
    days_to_roll,
    front_month_contract,
    get_roll_rule,
    next_roll_date,
    set_roll_rule_override,
)
from levelsheet.data.symbols import (
    format_contract_code,
    get_root_spec,
    parse_contract_code,
    resolve_symbol,
    to_polygon_ticker,
    to_yfinance_ticker,
)
from levelsheet.errors import (
    DataValidationError,
    ExportError,
    ProviderUnavailableError,
    RollCalendarError,
)
from levelsheet.models.schemas import validate_ohlc_df
from levelsheet.render.export_pdf import export_pdf_weasyprint, sheet_to_html
from levelsheet.render.export_png import export_png
from levelsheet.render.fonts import register_custom_fonts


def test_symbols_roundtrip() -> None:
    assert to_yfinance_ticker("ES") == "ES=F"
    assert to_polygon_ticker("ES") == "I:ES"
    assert resolve_symbol("ES", "yfinance") == "ES=F"
    assert resolve_symbol("ES", "polygon") == "I:ES"
    assert resolve_symbol("ES", "ib") == "ES"
    assert resolve_symbol("ES", "unknown") == "ES"
    spec = parse_contract_code("ESU26")
    assert spec.root == "ES" and spec.month == "U" and spec.year == 2026
    assert format_contract_code("ES", "U", 2026) == "ESU26"
    assert get_root_spec("ES").point_value == 50.0
    assert get_root_spec("UNKNOWNROOT").exchange == "CME"


def test_parse_invalid_contract() -> None:
    with pytest.raises(ValueError):
        parse_contract_code("!!!")


def test_roll_calendar_es() -> None:
    clear_roll_rule_overrides()
    rule = get_roll_rule("ES")
    assert rule.roll_reference == "volume_crossover"
    as_of = date(2026, 2, 1)
    code = front_month_contract("ES", as_of)
    assert code.startswith("ES")
    nxt = next_roll_date("ES", as_of)
    assert nxt >= as_of
    assert days_to_roll("ES", as_of) >= 0


def test_roll_calendar_missing() -> None:
    clear_roll_rule_overrides()
    with pytest.raises(RollCalendarError):
        get_roll_rule("NOTAROOT")


def test_roll_calendar_override() -> None:
    clear_roll_rule_overrides()
    set_roll_rule_override("XX", RollRule(["H", "M", "U", "Z"], 5, "fixed_calendar"))
    assert get_roll_rule("XX").days_before_first_notice == 5
    clear_roll_rule_overrides()


def test_roll_cl_fixed() -> None:
    clear_roll_rule_overrides()
    code = front_month_contract("CL", date(2026, 5, 1))
    assert code.startswith("CL")


def test_validate_ohlc_errors() -> None:
    with pytest.raises(DataValidationError):
        validate_ohlc_df(pd.DataFrame({"open": [1.0]}))
    idx = pd.DatetimeIndex(["2024-01-02", "2024-01-01"])
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
    with pytest.raises(DataValidationError):
        validate_ohlc_df(df)


def test_yfinance_available() -> None:
    assert YFinanceProvider().is_available() is True


def test_polygon_unavailable_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    p = PolygonProvider()
    assert p.is_available() is False
    with pytest.raises(ProviderUnavailableError):
        p.fetch_ohlc("ES", date(2024, 1, 1), date(2024, 1, 10), "1d")


def test_ib_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IB_ENABLED", "false")
    ib = IBProvider()
    assert ib.is_available() is False
    with pytest.raises(ProviderUnavailableError):
        ib.fetch_ohlc("ES", date(2024, 1, 1), date(2024, 1, 10), "1d")


def test_provider_chain() -> None:
    cfg = load_config()
    chain = get_provider_chain(cfg)
    assert any(p.name == "yfinance" for p in chain)


def test_export_png_error(tmp_path: Path) -> None:
    fig = Figure()
    # empty figure still writes something small — force bad path via permission?
    # Instead assert ExportError on sanity for tiny file by mocking
    bad = tmp_path / "x.png"
    bad.write_bytes(b"tiny")
    # Directly exercise ExportError path by calling with a figure that we then shrink check
    from levelsheet.errors import ExportError as EE

    with pytest.raises(EE):
        # write to a path under a file (not a dir)
        blocker = tmp_path / "notadir"
        blocker.write_text("x")
        export_png(fig, blocker / "out.png")


def test_register_fonts(tmp_path: Path) -> None:
    register_custom_fonts(tmp_path)
    (tmp_path / "fake.ttf").write_bytes(b"notafont")
    register_custom_fonts(tmp_path)


def test_weasyprint_export(tmp_path: Path) -> None:
    from levelsheet.models.schemas import SheetData
    from levelsheet.render.theme import Theme

    html = sheet_to_html(SheetData(root="ES", as_of_date="2026-01-01"), Theme())
    out = tmp_path / "w.pdf"
    try:
        export_pdf_weasyprint(html, out)
        assert out.exists()
    except ExportError:
        # weasyprint system libs may be incomplete in some envs
        pass
