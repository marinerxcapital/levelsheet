"""Unit tests for warning flags."""

from __future__ import annotations

from levelsheet.calc.warnings_flags import OHLCBar, is_ahdd, is_blud, is_false_day, is_rth_gap


def test_false_day() -> None:
    y = OHLCBar(open=100, high=105, low=95, close=102)
    t = OHLCBar(open=106, high=107, low=100, close=101)  # open above, close inside
    assert is_false_day(t, y) is True


def test_not_false_day() -> None:
    y = OHLCBar(open=100, high=105, low=95, close=102)
    t = OHLCBar(open=106, high=110, low=104, close=108)  # closed outside
    assert is_false_day(t, y) is False


def test_rth_gap() -> None:
    assert is_rth_gap(100.2, 100.0, threshold_pct=0.15) is True
    assert is_rth_gap(100.1, 100.0, threshold_pct=0.15) is False


def test_blud() -> None:
    y = OHLCBar(open=100, high=105, low=95, close=102)
    t = OHLCBar(open=96, high=104, low=94, close=103)  # undercut, green, near high
    assert is_blud(t, y) is True


def test_ahdd() -> None:
    y = OHLCBar(open=100, high=105, low=95, close=102)
    t = OHLCBar(open=104, high=107, low=96, close=97)  # exceeded high, red, near low
    assert is_ahdd(t, y) is True
