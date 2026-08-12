"""Unit tests for ATR / true range."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from levelsheet.calc.atr import atr_wilder, true_range


def _ohlc_frame(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"])


def test_atr_wilder_fixture() -> None:
    fixture_path = Path(__file__).parent.parent / "fixtures" / "expected_values.json"
    data = json.loads(fixture_path.read_text())
    atr_fix = data["atr_wilder_14"]
    df = _ohlc_frame([tuple(r) for r in atr_fix["ohlc"]])  # type: ignore[misc]
    atr = atr_wilder(df, length=14)
    assert atr.iloc[14] == pytest.approx(atr_fix["atr_at_index_14"], abs=1e-6)


def test_true_range_basic() -> None:
    df = _ohlc_frame(
        [
            (100, 102, 99, 101),
            (101, 103, 100, 102),
        ]
    )
    tr = true_range(df)
    assert tr.iloc[1] == pytest.approx(3.0)  # max(3, 2, 1)


@st.composite
def valid_ohlc(draw: st.DrawFn, n: int = 20) -> pd.DataFrame:
    rows = []
    price = draw(st.floats(min_value=50.0, max_value=200.0, allow_nan=False, allow_infinity=False))
    for _ in range(n):
        o = price
        amplitude = draw(st.floats(min_value=0.1, max_value=5.0, allow_nan=False, allow_infinity=False))
        h = o + amplitude
        l = o - amplitude
        c = draw(st.floats(min_value=l, max_value=h, allow_nan=False, allow_infinity=False))
        rows.append((o, h, l, c))
        price = c
    return _ohlc_frame(rows)


@given(df=valid_ohlc())
@settings(max_examples=25)
def test_atr_non_negative(df: pd.DataFrame) -> None:
    atr = atr_wilder(df, length=14)
    valid = atr.dropna()
    assert (valid >= 0).all()
