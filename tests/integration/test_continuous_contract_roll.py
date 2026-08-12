"""Integration test: ratio-adjusted continuous contract has zero discontinuity at rolls."""

from __future__ import annotations

from datetime import date

import pandas as pd

from levelsheet.data.continuous_contract import build_continuous_series
from levelsheet.data.roll_calendar import (
    RollRule,
    clear_roll_rule_overrides,
    set_roll_rule_override,
)


class SyntheticProvider:
    """Serves three contracts with known prices and a 10% roll gap."""

    name = "synthetic"

    def is_available(self) -> bool:
        return True

    def fetch_ohlc(self, symbol: str, start: date, end: date, interval: str) -> pd.DataFrame:
        # Contracts: TESH24, TESM24, TESU24 with closes that jump 10% at rolls
        prices = {
            "TESH24": 100.0,
            "TESM24": 110.0,  # 10% higher
            "TESU24": 121.0,  # another 10%
        }
        base = prices.get(symbol, 100.0)
        # Generate daily bars within [start, end]
        idx = pd.bdate_range(start, end)
        if len(idx) == 0:
            idx = pd.DatetimeIndex([pd.Timestamp(start)])
        rows = []
        for i, ts in enumerate(idx):
            c = base + i * 0.01
            rows.append(
                {
                    "open": c - 0.1,
                    "high": c + 0.2,
                    "low": c - 0.2,
                    "close": c,
                    "volume": 1000,
                    "contract": symbol,
                }
            )
        df = pd.DataFrame(rows, index=pd.DatetimeIndex(idx).normalize())
        df["volume"] = df["volume"].astype("Int64")
        return df


def test_continuous_contract_zero_discontinuity() -> None:
    clear_roll_rule_overrides()
    # Force known roll dates via fixed_calendar with months H,M,U
    rule = RollRule(
        ["H", "M", "U", "Z"], days_before_first_notice=0, roll_reference="fixed_calendar"
    )
    set_roll_rule_override("TES", rule)
    try:
        # Build with a provider that returns per-contract series
        # Monkeypatch front_month to return our synthetic codes by using root TES
        # and relying on roll calendar — for deterministic test, call adjust manually.
        provider = SyntheticProvider()

        # Build three segments manually and apply same algorithm expectations:
        # At each roll, ratio = old_close/new_close ≈ 100/110, 110/121
        from levelsheet.data import continuous_contract as cc

        # Patch _contract_sequence to return fixed segments
        def fake_seq(root, start, end, rule):  # type: ignore[no-untyped-def]
            return [
                ("TESH24", date(2024, 1, 2), date(2024, 2, 29)),
                ("TESM24", date(2024, 3, 1), date(2024, 5, 31)),
                ("TESU24", date(2024, 6, 3), date(2024, 8, 30)),
            ]

        original = cc._contract_sequence
        cc._contract_sequence = fake_seq  # type: ignore[assignment]
        try:
            continuous = build_continuous_series(
                "TES", provider, date(2024, 1, 2), date(2024, 8, 30), rule=rule
            )
        finally:
            cc._contract_sequence = original  # type: ignore[assignment]

        # Check discontinuities at segment boundaries (first day of new contracts)
        # After ratio adjustment, close just before roll ≈ close just after roll
        contracts = continuous["contract"].tolist()
        for i in range(1, len(continuous)):
            if contracts[i] != contracts[i - 1]:
                prev_c = float(continuous["close"].iloc[i - 1])
                new_c = float(continuous["close"].iloc[i])
                pct = abs(new_c - prev_c) / prev_c * 100
                assert pct < 0.01, f"discontinuity {pct:.4f}% at index {i}"
    finally:
        clear_roll_rule_overrides()
