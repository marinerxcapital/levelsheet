"""Unit tests for Elliott wave zigzag and projection."""

from __future__ import annotations

import pandas as pd
import pytest

from levelsheet.calc.elliott_wave import detect_swings_zigzag, elliott_wave_projection
from levelsheet.errors import InsufficientHistoryError


def _make_wave_df() -> pd.DataFrame:
    """Synthetic impulse with clear 3%+ swings."""
    closes = [
        100,
        105,
        110,
        115,
        120,  # up to high
        116,
        112,
        108,  # down >3%
        112,
        118,
        125,
        132,  # up
        128,
        122,
        118,  # down
        122,
        128,
        135,
        142,  # up
        138,
        132,
        128,  # down
        132,
        138,
        145,  # up
    ]
    rows = []
    for c in closes:
        rows.append({"open": c - 0.5, "high": c + 1.0, "low": c - 1.0, "close": float(c)})
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="B")
    return pd.DataFrame(rows, index=idx)


def test_detect_swings_alternating() -> None:
    swings = detect_swings_zigzag(_make_wave_df(), threshold_pct=3.0)
    assert len(swings) >= 2
    kinds = swings["kind"].tolist()
    for a, b in zip(kinds, kinds[1:]):
        assert a != b


def test_elliott_projection_requires_six() -> None:
    swings = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="B"),
            "price": [100.0, 110.0, 105.0],
            "kind": ["Low", "High", "Low"],
        }
    )
    with pytest.raises(InsufficientHistoryError):
        elliott_wave_projection(swings)


def test_elliott_projection_basic() -> None:
    swings = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=6, freq="B"),
            "price": [100.0, 110.0, 105.0, 125.0, 115.0, 130.0],
            "kind": ["Low", "High", "Low", "High", "Low", "High"],
        }
    )
    proj = elliott_wave_projection(swings)
    # wave1=10, wave3=20 > 10*1.618 → extended, ext=2.618
    # wave5_target = 115 + 1 * 10 * 2.618 = 141.18
    assert proj.extended_third is True
    assert proj.ext_ratio == pytest.approx(2.618)
    assert proj.wave5_target == pytest.approx(141.18)
