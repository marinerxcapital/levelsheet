"""Unit tests for bias classification."""

from __future__ import annotations

import math

from levelsheet.calc.bias import bias


def test_bias_long() -> None:
    assert bias(5100.0, 5000.0) == "LONG"


def test_bias_short() -> None:
    assert bias(4900.0, 5000.0) == "SHORT"


def test_bias_none_equal() -> None:
    assert bias(5000.0, 5000.0) == "NONE"


def test_bias_none_nan() -> None:
    assert bias(5000.0, float("nan")) == "NONE"
    assert bias(5000.0, math.nan) == "NONE"
