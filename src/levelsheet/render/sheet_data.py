"""Build SheetData from OHLC frames + config."""

from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd

from levelsheet.calc.atr import atr_wilder
from levelsheet.calc.autotrade import compute_autotrade_settings
from levelsheet.calc.bias import bias
from levelsheet.calc.elliott_wave import detect_swings_zigzag, elliott_wave_projection
from levelsheet.calc.extreme_moves import extreme_move_targets
from levelsheet.calc.fibonacci import fibonacci_levels
from levelsheet.calc.moving_averages import ema, projected_ma, sma
from levelsheet.calc.nr7_wr7 import is_nr7, is_wr7
from levelsheet.calc.pivots import camarilla_pivots, classic_pivots, woodie_pivots
from levelsheet.calc.warnings_flags import OHLCBar, is_ahdd, is_blud, is_false_day, is_rth_gap
from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.roll_calendar import days_to_roll
from levelsheet.data.symbols import get_root_spec
from levelsheet.errors import InsufficientHistoryError
from levelsheet.models.schemas import SheetData


def _pivot_fn(method: str):  # type: ignore[no-untyped-def]
    return {"classic": classic_pivots, "camarilla": camarilla_pivots, "woodie": woodie_pivots}[
        method
    ]


def _bar(row: pd.Series) -> OHLCBar:
    return OHLCBar(
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
    )


def build_sheet_data(
    root: str,
    as_of: date,
    daily: pd.DataFrame,
    weekly: Optional[pd.DataFrame],
    monthly: Optional[pd.DataFrame],
    config: LevelSheetConfig,
) -> SheetData:
    """Compute all levels and assemble SheetData for rendering."""
    spec = get_root_spec(root)
    daily = daily.sort_index()
    # Use last complete bar as reference (prior day for next-day levels)
    last = daily.iloc[-1]
    prev = daily.iloc[-2] if len(daily) >= 2 else last
    pivot_fn = _pivot_fn(config.pivots.method)
    daily_piv = pivot_fn(float(last["high"]), float(last["low"]), float(last["close"]))

    weekly_piv = None
    if weekly is not None and len(weekly) > 0:
        w = weekly.iloc[-1]
        weekly_piv = pivot_fn(float(w["high"]), float(w["low"]), float(w["close"]))
    monthly_piv = None
    if monthly is not None and len(monthly) > 0:
        m = monthly.iloc[-1]
        monthly_piv = pivot_fn(float(m["high"]), float(m["low"]), float(m["close"]))

    ma_fn = sma if config.moving_averages.type == "sma" else ema
    ma_values: dict[int, float] = {}
    ma_bias: dict[int, str] = {}
    projected: dict[int, tuple[float, float]] = {}
    close = daily["close"]
    for length in config.moving_averages.lengths:
        series = ma_fn(close, length)
        val = float(series.iloc[-1]) if not pd.isna(series.iloc[-1]) else float("nan")
        if pd.isna(val):
            # Panel renderer raises; we store NaN and mark NONE
            ma_values[length] = float("nan")
            ma_bias[length] = "NONE"
        else:
            ma_values[length] = val
            ma_bias[length] = bias(float(last["close"]), val)
            try:
                proj = projected_ma(series)
                projected[length] = (round(val, 2), proj)
            except InsufficientHistoryError:
                pass

    atr_series = atr_wilder(daily, length=config.atr.length)
    atr_val = float(atr_series.iloc[-1]) if not pd.isna(atr_series.iloc[-1]) else None
    atr_5 = float(atr_wilder(daily, length=5).iloc[-1]) if len(daily) >= 5 else atr_val

    try:
        nr7 = is_nr7(daily)
    except InsufficientHistoryError:
        nr7 = False
    try:
        wr7 = is_wr7(daily)
    except InsufficientHistoryError:
        wr7 = False

    hi_7 = float(daily["high"].tail(7).max()) if len(daily) >= 7 else None
    lo_7 = float(daily["low"].tail(7).min()) if len(daily) >= 7 else None
    hi_20 = float(daily["high"].tail(20).max()) if len(daily) >= 20 else None
    lo_20 = float(daily["low"].tail(20).min()) if len(daily) >= 20 else None

    # Long-term fib from zigzag swings
    swings = detect_swings_zigzag(
        daily, threshold_pct=config.fibonacci.long_term_swing_threshold_pct
    )
    long_fib: dict[str, float] = {}
    if len(swings) >= 2:
        a, b = swings.iloc[-2], swings.iloc[-1]
        hi = max(float(a["price"]), float(b["price"]))
        lo = min(float(a["price"]), float(b["price"]))
        direction = "down" if float(b["price"]) < float(a["price"]) else "up"
        long_fib = fibonacci_levels(hi, lo, direction)  # type: ignore[arg-type]

    # Daily fib from last 20-bar swing
    window = daily.tail(20)
    d_hi = float(window["high"].max())
    d_lo = float(window["low"].min())
    daily_fib = fibonacci_levels(d_hi, d_lo, "down")

    extremes = extreme_move_targets(float(last["close"]))

    point_value = config.symbols.point_values.get(root, spec.point_value)
    auto = None
    if atr_val is not None:
        auto = compute_autotrade_settings(atr_val, root, config.autotrade, point_value)

    elliott = None
    try:
        ew_swings = detect_swings_zigzag(
            daily, threshold_pct=config.elliott_wave.zigzag_threshold_pct
        )
        if len(ew_swings) >= 6:
            elliott = elliott_wave_projection(ew_swings)
    except InsufficientHistoryError:
        elliott = None

    today = _bar(last)
    yesterday = _bar(prev)
    warnings = {
        "false_day": is_false_day(today, yesterday),
        "rth_gap": is_rth_gap(today.open, yesterday.close, config.warnings.rth_gap_threshold_pct),
        "blud": is_blud(today, yesterday, config.warnings.close_proximity_pct),
        "ahdd": is_ahdd(today, yesterday, config.warnings.close_proximity_pct),
    }

    contract = str(last.get("contract", root))
    try:
        dtr = days_to_roll(root, as_of)
    except Exception:  # noqa: BLE001
        dtr = 999

    return SheetData(
        root=root.upper(),
        as_of_date=as_of.isoformat(),
        contract=contract,
        days_to_roll=dtr,
        decimals=spec.default_pivot_decimals,
        company_name=config.branding.company_name,
        footer_text=config.branding.footer_text,
        logo_path=config.branding.logo_path,
        daily_pivots=daily_piv,
        weekly_pivots=weekly_piv,
        monthly_pivots=monthly_piv,
        today_bar=today,
        ma_values=ma_values,
        ma_bias=ma_bias,
        atr_value=atr_val,
        atr_5d=atr_5,
        nr7=nr7,
        wr7=wr7,
        hi_7=hi_7,
        lo_7=lo_7,
        hi_20=hi_20,
        lo_20=lo_20,
        long_term_fib=long_fib,
        daily_fib=daily_fib,
        extreme_moves=extremes,
        autotrade=auto,
        elliott=elliott,
        projected_mas=projected,
        warnings=warnings,
    )
