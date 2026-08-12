"""Unit tests for SMA/EMA/projected_ma."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from levelsheet.calc.moving_averages import ema, projected_ma, sma
from levelsheet.errors import InsufficientHistoryError


def test_sma_basic() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = sma(s, 3)
    assert len(result) == 5
    assert pd.isna(result.iloc[0]) and pd.isna(result.iloc[1])
    assert result.iloc[2] == pytest.approx(2.0)
    assert result.iloc[4] == pytest.approx(4.0)


def test_ema_basic() -> None:
    s = pd.Series([float(i) for i in range(1, 11)])
    result = ema(s, 3)
    assert len(result) == 10
    assert pd.isna(result.iloc[0]) and pd.isna(result.iloc[1])
    assert not pd.isna(result.iloc[2])


def test_projected_ma() -> None:
    s = pd.Series([np.nan, np.nan, 10.0, 12.0])
    assert projected_ma(s) == pytest.approx(14.0)


def test_projected_ma_insufficient() -> None:
    with pytest.raises(InsufficientHistoryError):
        projected_ma(pd.Series([np.nan, 1.0]))


@given(n=st.integers(min_value=5, max_value=40), length=st.integers(min_value=2, max_value=10))
@settings(max_examples=30)
def test_sma_ema_length_and_leading_nans(n: int, length: int) -> None:
    series = pd.Series(np.linspace(1.0, float(n), n))
    s = sma(series, length)
    e = ema(series, length)
    assert len(s) == n
    assert len(e) == n
    assert s.iloc[: length - 1].isna().all()
