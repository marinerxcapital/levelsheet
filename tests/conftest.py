"""Shared pytest fixtures. Expanded in Phase 1–2."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to tests/fixtures."""
    return FIXTURES
