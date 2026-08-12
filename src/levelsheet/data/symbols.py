"""Futures symbol resolution, month codes, and root specifications."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from loguru import logger

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

_QUARTERLY = ["H", "M", "U", "Z"]
_ALL_MONTHS = list(MONTH_CODES.keys())


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
    contract_months: list[str] = field(default_factory=lambda: list(_QUARTERLY))


DEFAULT_ROOT_SPEC = RootSpec(
    exchange="CME",
    point_value=1.0,
    tick_size=0.01,
    default_pivot_decimals=2,
    contract_months=list(_QUARTERLY),
)

SUPPORTED_ROOTS: dict[str, RootSpec] = {
    "ES": RootSpec("CME", 50.0, 0.25, 2, list(_QUARTERLY)),
    "NQ": RootSpec("CME", 20.0, 0.25, 2, list(_QUARTERLY)),
    "RTY": RootSpec("CME", 50.0, 0.10, 2, list(_QUARTERLY)),
    "YM": RootSpec("CBOT", 5.0, 1.0, 2, list(_QUARTERLY)),
    "CL": RootSpec("NYMEX", 1000.0, 0.01, 2, list(_ALL_MONTHS)),
    "NG": RootSpec("NYMEX", 10000.0, 0.001, 2, list(_ALL_MONTHS)),
    "GC": RootSpec("COMEX", 100.0, 0.10, 2, ["G", "J", "M", "Q", "V", "Z"]),
    "SI": RootSpec("COMEX", 5000.0, 0.005, 2, ["H", "K", "N", "U", "Z"]),
    "HG": RootSpec("COMEX", 25000.0, 0.0005, 2, ["H", "K", "N", "U", "Z"]),
    "ZB": RootSpec("CBOT", 1000.0, 1 / 32, 2, list(_QUARTERLY)),
    "ZN": RootSpec("CBOT", 1000.0, 1 / 64, 2, list(_QUARTERLY)),
    "ZF": RootSpec("CBOT", 1000.0, 1 / 128, 2, list(_QUARTERLY)),
    "ZT": RootSpec("CBOT", 2000.0, 1 / 128, 2, list(_QUARTERLY)),
    "6E": RootSpec("CME", 125000.0, 0.00005, 4, list(_QUARTERLY)),
    "6J": RootSpec("CME", 12500000.0, 0.0000005, 4, list(_QUARTERLY)),
    "6B": RootSpec("CME", 62500.0, 0.0001, 4, list(_QUARTERLY)),
    "6A": RootSpec("CME", 100000.0, 0.0001, 4, list(_QUARTERLY)),
    "6C": RootSpec("CME", 100000.0, 0.00005, 4, list(_QUARTERLY)),
    "ZC": RootSpec("CBOT", 50.0, 0.25, 2, ["H", "K", "N", "U", "Z"]),
    "ZS": RootSpec("CBOT", 50.0, 0.25, 2, ["F", "H", "K", "N", "Q", "U", "X"]),
    "ZW": RootSpec("CBOT", 50.0, 0.25, 2, ["H", "K", "N", "U", "Z"]),
}


def get_root_spec(root: str) -> RootSpec:
    """Return RootSpec for root, falling back to DEFAULT_ROOT_SPEC with a warning."""
    key = root.upper()
    if key not in SUPPORTED_ROOTS:
        logger.warning("Unknown root={!r}; using default RootSpec", root)
        return DEFAULT_ROOT_SPEC
    return SUPPORTED_ROOTS[key]


def to_yfinance_ticker(root: str) -> str:
    """Format root as yfinance continuous front-month ticker (e.g. ES → ES=F)."""
    return f"{root.upper()}=F"


def to_polygon_ticker(root: str) -> str:
    """Format root as Polygon continuous futures ticker (e.g. ES → I:ES)."""
    # Polygon futures continuous: I:{root} is a common convention for indices;
    # document choice in DECISIONS.md. Spec mentioned C:ES style — use I: for futures.
    return f"I:{root.upper()}"


def resolve_symbol(root: str, provider: str) -> str:
    """Map bare root to provider-specific continuous ticker string."""
    provider_l = provider.lower()
    if provider_l in ("yfinance", "yf"):
        return to_yfinance_ticker(root)
    if provider_l in ("polygon",):
        return to_polygon_ticker(root)
    if provider_l in ("ib", "ibkr"):
        return root.upper()
    logger.warning("Unknown provider={!r}; returning bare root", provider)
    return root.upper()


_CONTRACT_RE = re.compile(r"^([A-Z0-9]+?)([FGHJKMNQUVXZ])(\d{1,4})$")


def parse_contract_code(code: str) -> ContractSpec:
    """Parse e.g. ESU26 / ESU2026 into root/month/year."""
    m = _CONTRACT_RE.match(code.upper())
    if not m:
        raise ValueError(f"Invalid contract code: {code!r}")
    root, month, year_s = m.group(1), m.group(2), m.group(3)
    year = int(year_s)
    if year < 100:
        year += 2000
    return ContractSpec(root=root, month=month, year=year)


def format_contract_code(root: str, month: str, year: int) -> str:
    """Format root/month/year into compact contract code (2-digit year)."""
    yy = year % 100
    return f"{root.upper()}{month.upper()}{yy:02d}"
