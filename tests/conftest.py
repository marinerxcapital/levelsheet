"""Shared pytest fixtures. Expanded in Phase 1–2."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to tests/fixtures."""
    return FIXTURES


@pytest.fixture
def repo_root() -> Path:
    """Return repository root (portable across local, CI, and cloud agents)."""
    return REPO_ROOT
