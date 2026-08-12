"""Unit tests for extreme move targets."""

from __future__ import annotations

import pytest

from levelsheet.calc.extreme_moves import extreme_move_targets


def test_extreme_move_targets() -> None:
    targets = extreme_move_targets(5000.0)
    assert targets["+1.0%"] == pytest.approx(5050.0)
    assert targets["-1.0%"] == pytest.approx(4950.0)
    assert targets["+5.0%"] == pytest.approx(5250.0)
    assert targets["-0.5%"] == pytest.approx(4975.0)
    assert len(targets) == 12
