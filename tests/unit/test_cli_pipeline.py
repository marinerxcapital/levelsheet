"""CLI and pipeline smoke tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from levelsheet.cli.__main__ import build_parser, main
from levelsheet.config.loader import load_config
from levelsheet.logging_config import configure_logging
from levelsheet.pipeline import (
    apply_roll_rule_json,
    build_sheet_bytes,
    export_sheet_files,
    generate_figure,
    load_fixture_frames,
    parse_date,
)


def test_configure_logging(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "logs").mkdir()
    configure_logging(debug=True)
    configure_logging(debug=False)


def test_parse_date() -> None:
    assert parse_date(None) == date.today()
    assert parse_date("2026-08-12") == date(2026, 8, 12)


def test_load_fixture_frames() -> None:
    d, w, m = load_fixture_frames("ES")
    assert len(d) >= 200
    assert len(w) > 0 and len(m) > 0


def test_generate_figure_from_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/workspace"))
    cfg = load_config()
    cfg.data.cache.dir = str(tmp_path / "cache")
    data, fig = generate_figure("ES", date(2026, 2, 25), cfg)
    assert data.root == "ES"
    assert fig is not None


def test_export_sheet_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/workspace"))
    cfg = load_config()
    cfg.data.cache.dir = str(tmp_path / "cache")
    paths = export_sheet_files("ES", date(2026, 2, 25), cfg, tmp_path / "out", ["pdf", "png"])
    assert paths["pdf"].exists() and paths["png"].exists()


def test_build_sheet_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/workspace"))
    cfg = load_config()
    cfg.data.cache.dir = str(tmp_path / "cache")
    fig, pdf_b, png_b = build_sheet_bytes("ES", date(2026, 2, 25), cfg)
    assert len(pdf_b) > 1000 and len(png_b) > 50_000


def test_apply_roll_rule_json() -> None:
    apply_roll_rule_json(
        "ZZ",
        '{"contract_months":["H","M","U","Z"],"days_before_first_notice":5,'
        '"roll_reference":"fixed_calendar"}',
    )


def test_cli_config_show(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["levelsheet", "config", "show"])
    assert main() == 0


def test_cli_generate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/workspace"))
    out = tmp_path / "output"
    monkeypatch.setattr(
        "sys.argv",
        [
            "levelsheet",
            "generate",
            "ES",
            "--date",
            "2026-02-25",
            "--format",
            "png",
            "--output-dir",
            str(out),
        ],
    )
    assert main() == 0
    assert any(out.joinpath("png").glob("*.png"))


def test_cli_book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/workspace"))
    out = tmp_path / "book.pdf"
    monkeypatch.setattr(
        "sys.argv",
        [
            "levelsheet",
            "book",
            "--date",
            "2026-02-25",
            "--symbols",
            "ES",
            "--output",
            str(out),
        ],
    )
    assert main() == 0
    assert out.exists()


def test_build_parser_has_subcommands() -> None:
    parser = build_parser()
    assert parser.parse_args(["config", "show"]).command == "config"
