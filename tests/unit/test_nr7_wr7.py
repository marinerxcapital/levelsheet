"""Unit tests for NR7 / WR7."""

from __future__ import annotations

import pandas as pd
import pytest

from levelsheet.calc.nr7_wr7 import is_nr7, is_wr7
from levelsheet.errors import InsufficientHistoryError


def _ranges_df(ranges: list[float]) -> pd.DataFrame:
    rows = []
    for r in ranges:
        mid = 100.0
        rows.append({"open": mid, "high": mid + r / 2, "low": mid - r / 2, "close": mid})
    return pd.DataFrame(rows)


def test_is_nr7_true() -> None:
    df = _ranges_df([5, 4, 6, 3, 7, 4, 2])
    assert is_nr7(df) is True
    assert is_wr7(df) is False


def test_is_wr7_true() -> None:
    df = _ranges_df([5, 4, 6, 3, 7, 4, 9])
    assert is_wr7(df) is True
    assert is_nr7(df) is False


def test_nr7_insufficient() -> None:
    with pytest.raises(InsufficientHistoryError):
        is_nr7(_ranges_df([1, 2, 3]))
