"""Sheet grid layout constants (80×120 unit GridSpec). Stub panels wired in Phase 3."""

from __future__ import annotations

from typing import NamedTuple


class GridSpecRegion(NamedTuple):
    """Inclusive-exclusive style region: (row_start, row_end, col_start, col_end)."""

    row_start: int
    row_end: int
    col_start: int
    col_end: int


SHEET_LAYOUT: dict[str, GridSpecRegion] = {
    "header": GridSpecRegion(0, 8, 0, 120),
    "daily_pivots": GridSpecRegion(9, 33, 0, 24),
    "center_ohlc_ma": GridSpecRegion(9, 33, 25, 60),
    "mini_candlestick": GridSpecRegion(9, 33, 61, 70),
    "weekly_panel": GridSpecRegion(9, 20, 71, 95),
    "monthly_panel": GridSpecRegion(9, 20, 96, 120),
    "atr_nr7_panel": GridSpecRegion(21, 33, 71, 95),
    "hilo_7_20_panel": GridSpecRegion(21, 33, 96, 120),
    "long_term_fib": GridSpecRegion(34, 58, 0, 36),
    "daily_fib_extreme": GridSpecRegion(34, 58, 37, 72),
    "bias_panel": GridSpecRegion(34, 50, 73, 120),
    "autotrade_panel": GridSpecRegion(51, 58, 73, 120),
    "elliott_panel": GridSpecRegion(59, 74, 0, 55),
    "projected_ma_panel": GridSpecRegion(59, 74, 56, 82),
    "warnings_panel": GridSpecRegion(59, 74, 83, 120),
    "footer": GridSpecRegion(75, 80, 0, 120),
}

FIGSIZE = (17, 11)
DPI = 300
