"""Unit tests for classic/camarilla/woodie pivots."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from levelsheet.calc.pivots import camarilla_pivots, classic_pivots, woodie_pivots


def test_classic_pivots_fixture() -> None:
    result = classic_pivots(5100.00, 5060.00, 5080.00)
    assert result.p == pytest.approx(5080.00, abs=1e-6)
    assert result.r1 == pytest.approx(5100.00, abs=1e-6)
    assert result.s1 == pytest.approx(5060.00, abs=1e-6)
    assert result.r2 == pytest.approx(5120.00, abs=1e-6)
    assert result.s2 == pytest.approx(5040.00, abs=1e-6)
    assert result.r3 == pytest.approx(5140.00, abs=1e-6)
    assert result.s3 == pytest.approx(5020.00, abs=1e-6)


def test_camarilla_pivots_fixture() -> None:
    result = camarilla_pivots(5100.00, 5060.00, 5080.00)
    assert round(result.r1, 2) == pytest.approx(5083.67, abs=1e-6)
    assert round(result.r2, 2) == pytest.approx(5087.33, abs=1e-6)
    assert round(result.r3, 2) == pytest.approx(5091.00, abs=1e-6)
    assert round(result.r4, 2) == pytest.approx(5102.00, abs=1e-6)
    assert round(result.s1, 2) == pytest.approx(5076.33, abs=1e-6)
    assert round(result.s2, 2) == pytest.approx(5072.67, abs=1e-6)
    assert round(result.s3, 2) == pytest.approx(5069.00, abs=1e-6)
    assert round(result.s4, 2) == pytest.approx(5058.00, abs=1e-6)
    assert result.p == pytest.approx(5080.00, abs=1e-6)


def test_woodie_pivots_fixture() -> None:
    result = woodie_pivots(5100.00, 5060.00, 5080.00)
    assert result.p == pytest.approx(5080.00, abs=1e-6)
    assert result.r1 == pytest.approx(5100.00, abs=1e-6)
    assert result.s1 == pytest.approx(5060.00, abs=1e-6)
    assert result.r2 == pytest.approx(5120.00, abs=1e-6)
    assert result.s2 == pytest.approx(5040.00, abs=1e-6)


@given(
    low=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    width=st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False),
    close_frac=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=50)
def test_classic_pivots_properties(low: float, width: float, close_frac: float) -> None:
    high = low + width
    close = low + width * close_frac
    result = classic_pivots(high, low, close)
    # Spec said R1+S1==2P; mathematically R2+S2==2P always. R1+S1==2P only when C midpoint.
    assert result.r2 + result.s2 == pytest.approx(2 * result.p, abs=1e-6)
    assert result.r3 is not None and result.s3 is not None
    assert result.r3 > result.r2 > result.r1 > result.p > result.s1 > result.s2 > result.s3
