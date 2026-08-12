"""Unit tests for autotrade settings."""

from __future__ import annotations

import pytest

from levelsheet.calc.autotrade import compute_autotrade_settings
from levelsheet.config.schema import AutoTradeConfig


def test_compute_autotrade_settings() -> None:
    cfg = AutoTradeConfig()
    result = compute_autotrade_settings(atr_value=20.0, root="ES", config=cfg, point_value=50.0)
    assert result.max_stop == pytest.approx(20.0)
    assert result.trail == pytest.approx(10.0)
    assert result.max_target == pytest.approx(40.0)
    assert result.max_risk_dollars == pytest.approx(1000.0)
    assert result.side == "BOTH"
    assert result.size == 1
    assert result.scale_out == pytest.approx(50.0)
