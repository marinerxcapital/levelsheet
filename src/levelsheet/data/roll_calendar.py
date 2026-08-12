"""Futures roll calendar rules and front-month resolution. Stub — Phase 2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass(frozen=True)
class RollRule:
    """Roll timing rule for a futures root."""

    contract_months: list[str]
    days_before_first_notice: int
    roll_reference: Literal["volume_crossover", "fixed_calendar"]


ROLL_CALENDAR: dict[str, RollRule] = {}


def next_roll_date(root: str, as_of: date) -> date:
    """Compute next roll date for root. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


def front_month_contract(root: str, as_of: date) -> str:
    """Resolve front-month contract code as of date. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")
