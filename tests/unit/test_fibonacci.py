"""Unit tests for Fibonacci levels."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from levelsheet.calc.fibonacci import fibonacci_levels


def test_fibonacci_levels_fixture_down() -> None:
    levels = fibonacci_levels(5200.00, 4900.00, "down")
    expected = {
        "0.0%": 5200.00,
        "23.6%": 5129.20,
        "38.2%": 5085.40,
        "50.0%": 5050.00,
        "61.8%": 5014.60,
        "76.4%": 4970.80,
        "100.0%": 4900.00,
        "127.2%": 4818.40,
        "161.8%": 4714.60,
        "200.0%": 4600.00,
        # Spec listed 4415.40; formula swing_low - rng*(2.618-1) = 4900 - 485.4 = 4414.60
        "261.8%": 4414.60,
    }
    for k, v in expected.items():
        assert levels[k] == pytest.approx(v, abs=1e-6)


@given(
    swing_low=st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    width=st.floats(min_value=0.01, max_value=2000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=40)
def test_fibonacci_retracements_within_range(swing_low: float, width: float) -> None:
    swing_high = swing_low + width
    levels = fibonacci_levels(swing_high, swing_low, "down")
    for key in ["0.0%", "23.6%", "38.2%", "50.0%", "61.8%", "76.4%", "100.0%"]:
        # round(..., 2) can nudge endpoints by ≤0.01
        assert swing_low - 0.01 <= levels[key] <= swing_high + 0.01
