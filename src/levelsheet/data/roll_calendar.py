"""Futures roll calendar rules and front-month resolution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal, Optional

from loguru import logger

from levelsheet.data.symbols import MONTH_CODES, format_contract_code
from levelsheet.errors import RollCalendarError


@dataclass(frozen=True)
class RollRule:
    """Roll timing rule for a futures root."""

    contract_months: list[str]
    days_before_first_notice: int
    roll_reference: Literal["volume_crossover", "fixed_calendar"]


ROLL_CALENDAR: dict[str, RollRule] = {
    "ES": RollRule(["H", "M", "U", "Z"], 8, "volume_crossover"),
    "NQ": RollRule(["H", "M", "U", "Z"], 8, "volume_crossover"),
    "RTY": RollRule(["H", "M", "U", "Z"], 8, "volume_crossover"),
    "YM": RollRule(["H", "M", "U", "Z"], 8, "volume_crossover"),
    "CL": RollRule(
        ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"], 5, "fixed_calendar"
    ),
    "NG": RollRule(
        ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"], 3, "fixed_calendar"
    ),
    "GC": RollRule(["G", "J", "M", "Q", "V", "Z"], 5, "volume_crossover"),
    "SI": RollRule(["H", "K", "N", "U", "Z"], 5, "volume_crossover"),
    "HG": RollRule(["H", "K", "N", "U", "Z"], 5, "volume_crossover"),
    "ZB": RollRule(["H", "M", "U", "Z"], 10, "fixed_calendar"),
    "ZN": RollRule(["H", "M", "U", "Z"], 10, "fixed_calendar"),
    "6E": RollRule(["H", "M", "U", "Z"], 6, "volume_crossover"),
    "6J": RollRule(["H", "M", "U", "Z"], 6, "volume_crossover"),
    "ZC": RollRule(["H", "K", "N", "U", "Z"], 7, "fixed_calendar"),
    "ZS": RollRule(["F", "H", "K", "N", "Q", "U", "X"], 7, "fixed_calendar"),
    "ZW": RollRule(["H", "K", "N", "U", "Z"], 7, "fixed_calendar"),
}

_OVERRIDE: dict[str, RollRule] = {}


def set_roll_rule_override(root: str, rule: RollRule) -> None:
    """Register an inline RollRule override (e.g. from --roll-rule-json)."""
    _OVERRIDE[root.upper()] = rule


def clear_roll_rule_overrides() -> None:
    """Clear all roll rule overrides (tests)."""
    _OVERRIDE.clear()


def get_roll_rule(root: str) -> RollRule:
    """Return roll rule for root or raise RollCalendarError."""
    key = root.upper()
    if key in _OVERRIDE:
        return _OVERRIDE[key]
    if key in ROLL_CALENDAR:
        return ROLL_CALENDAR[key]
    raise RollCalendarError(
        f"No roll calendar entry for root={key!r}; supply --roll-rule-json"
    )


def _is_business_day(d: date) -> bool:
    return d.weekday() < 5


def _add_business_days(d: date, n: int) -> date:
    """Add n business days (n may be negative)."""
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    cur = d
    while remaining:
        cur += timedelta(days=step)
        if _is_business_day(cur):
            remaining -= 1
    return cur


def _third_friday(year: int, month: int) -> date:
    """Return the third Friday of year/month."""
    d = date(year, month, 1)
    while d.weekday() != 4:
        d += timedelta(days=1)
    return d + timedelta(weeks=2)


def _first_business_day(year: int, month: int) -> date:
    d = date(year, month, 1)
    while not _is_business_day(d):
        d += timedelta(days=1)
    return d


def _contract_month_year_sequence(
    rule: RollRule, start_year: int, end_year: int
) -> list[tuple[str, int]]:
    seq: list[tuple[str, int]] = []
    for year in range(start_year, end_year + 1):
        for m in rule.contract_months:
            seq.append((m, year))
    return seq


def _roll_date_for_contract(rule: RollRule, month_code: str, year: int) -> date:
    month_num = MONTH_CODES[month_code]
    if rule.roll_reference == "volume_crossover":
        # N business days before third-Friday-of-contract-month
        expiry = _third_friday(year, month_num)
        return _add_business_days(expiry, -rule.days_before_first_notice)
    # fixed_calendar: N business days before first business day of contract month
    first_bd = _first_business_day(year, month_num)
    return _add_business_days(first_bd, -rule.days_before_first_notice)


def front_month_contract(root: str, as_of: date, rule: Optional[RollRule] = None) -> str:
    """Resolve front-month contract code as of date."""
    rule = rule or get_roll_rule(root)
    candidates = _contract_month_year_sequence(rule, as_of.year - 1, as_of.year + 2)
    front: Optional[tuple[str, int]] = None
    for month_code, year in candidates:
        roll = _roll_date_for_contract(rule, month_code, year)
        if roll >= as_of:
            front = (month_code, year)
            break
    if front is None:
        month_code, year = candidates[-1]
        idx = rule.contract_months.index(month_code)
        if idx + 1 < len(rule.contract_months):
            front = (rule.contract_months[idx + 1], year)
        else:
            front = (rule.contract_months[0], year + 1)
    code = format_contract_code(root, front[0], front[1])
    logger.debug("front_month_contract(root={}, as_of={}) -> {}", root, as_of, code)
    return code


def next_roll_date(root: str, as_of: date, rule: Optional[RollRule] = None) -> date:
    """Compute next roll date for root on or after as_of."""
    rule = rule or get_roll_rule(root)
    candidates = _contract_month_year_sequence(rule, as_of.year - 1, as_of.year + 2)
    for month_code, year in candidates:
        roll = _roll_date_for_contract(rule, month_code, year)
        if roll >= as_of:
            logger.debug("next_roll_date(root={}, as_of={}) -> {}", root, as_of, roll)
            return roll
    month_code, year = candidates[-1]
    idx = rule.contract_months.index(month_code)
    if idx + 1 < len(rule.contract_months):
        nxt = (rule.contract_months[idx + 1], year)
    else:
        nxt = (rule.contract_months[0], year + 1)
    roll = _roll_date_for_contract(rule, nxt[0], nxt[1])
    logger.debug("next_roll_date(root={}, as_of={}) -> {}", root, as_of, roll)
    return roll


def days_to_roll(root: str, as_of: date) -> int:
    """Calendar days until next roll."""
    return (next_roll_date(root, as_of) - as_of).days
