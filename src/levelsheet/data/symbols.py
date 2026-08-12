"""Futures symbol resolution, month codes, and root specifications. Stub — Phase 2."""

from __future__ import annotations

from dataclasses import dataclass, field


MONTH_CODES: dict[str, int] = {
    "F": 1,
    "G": 2,
    "H": 3,
    "J": 4,
    "K": 5,
    "M": 6,
    "N": 7,
    "Q": 8,
    "U": 9,
    "V": 10,
    "X": 11,
    "Z": 12,
}
CODE_FOR_MONTH: dict[int, str] = {v: k for k, v in MONTH_CODES.items()}


@dataclass(frozen=True)
class ContractSpec:
    """Parsed futures contract identity."""

    root: str
    month: str
    year: int


@dataclass(frozen=True)
class RootSpec:
    """Per-root exchange and contract metadata."""

    exchange: str
    point_value: float
    tick_size: float
    default_pivot_decimals: int
    contract_months: list[str] = field(default_factory=lambda: ["H", "M", "U", "Z"])


SUPPORTED_ROOTS: dict[str, RootSpec] = {}


def resolve_symbol(root: str, provider: str) -> str:
    """Map bare root to provider-specific ticker. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


def to_yfinance_ticker(root: str) -> str:
    """Format root as yfinance continuous ticker. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


def to_polygon_ticker(root: str) -> str:
    """Format root as Polygon futures ticker. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


def parse_contract_code(code: str) -> ContractSpec:
    """Parse e.g. ESU26 into root/month/year. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")


def format_contract_code(root: str, month: str, year: int) -> str:
    """Format root/month/year into contract code. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")
