"""Config loader and theme override tests."""

from __future__ import annotations

import os
from pathlib import Path

from levelsheet.config.loader import load_config
from levelsheet.plugins.registry import REGISTRY
from levelsheet.models.schemas import SheetData


def test_load_defaults() -> None:
    cfg = load_config()
    assert cfg.theme.bullish == "#1B7A3D"
    assert cfg.branding.company_name == "BPTC 26 LLC"


def test_levelsheet_yaml_override(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.chdir(tmp_path)
    (tmp_path / "levelsheet.yaml").write_text("theme:\n  bullish: \"#00FF00\"\n")
    cfg = load_config()
    assert cfg.theme.bullish == "#00FF00"


def test_env_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LEVELSHEET__THEME__BEARISH", "#ABCDEF")
    cfg = load_config()
    assert cfg.theme.bearish.upper() == "#ABCDEF"


def test_plugin_annotate_root() -> None:
    data = SheetData(root="ES", as_of_date="2026-01-01")
    out = REGISTRY.apply_all(data, ["annotate_root"])
    assert out.extras.get("annotated_root") == "ES"
