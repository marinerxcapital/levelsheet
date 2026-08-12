"""Ratio-adjusted continuous futures contract construction."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import pandas as pd
from loguru import logger

from levelsheet.data.providers.base import DataProvider
from levelsheet.data.roll_calendar import (
    RollRule,
    _roll_date_for_contract,
    front_month_contract,
    get_roll_rule,
)
from levelsheet.data.symbols import parse_contract_code
from levelsheet.models.schemas import validate_ohlc_df


def _contract_sequence(
    root: str, start: date, end: date, rule: RollRule
) -> list[tuple[str, date, date]]:
    """Return list of (contract_code, segment_start, segment_end) covering [start, end]."""
    segments: list[tuple[str, date, date]] = []
    cursor = start
    safety = 0
    while cursor <= end and safety < 500:
        safety += 1
        code = front_month_contract(root, cursor, rule)
        spec = parse_contract_code(code)
        roll = _roll_date_for_contract(rule, spec.month, spec.year)
        seg_end = min(end, roll)
        if seg_end < cursor:
            # Already past roll — step forward one day
            cursor = cursor + timedelta(days=1)
            continue
        segments.append((code, cursor, seg_end))
        cursor = seg_end + timedelta(days=1)
    return segments


def build_continuous_series(
    root: str,
    provider: DataProvider,
    start: date,
    end: date,
    rule: Optional[RollRule] = None,
) -> pd.DataFrame:
    """Build ratio-adjusted continuous OHLC series.

    Walks backwards from the most recent contract; at each roll boundary
    multiplies earlier segments by adjustment_ratio =
    old_contract_close_on_roll / new_contract_close_on_roll.
    """
    rule = rule or get_roll_rule(root)
    segments = _contract_sequence(root, start, end, rule)
    if not segments:
        return pd.DataFrame(
            columns=["open", "high", "low", "close", "volume", "contract"]
        )

    frames: list[pd.DataFrame] = []
    for code, seg_start, seg_end in segments:
        raw = provider.fetch_ohlc(code, seg_start, seg_end, "1d")
        part = raw.copy()
        part["contract"] = code
        frames.append(part)

    # Ratio-adjust walking backwards
    adjusted: list[pd.DataFrame] = [frames[-1].copy()]
    cumulative = 1.0
    for i in range(len(frames) - 2, -1, -1):
        old_df = frames[i]
        new_df = frames[i + 1]
        # roll boundary = last date of old segment
        roll_date = old_df.index.max()
        old_close = float(old_df.loc[roll_date, "close"]) if roll_date in old_df.index else float(old_df["close"].iloc[-1])
        # new contract close on/near roll date
        if roll_date in new_df.index:
            new_close = float(new_df.loc[roll_date, "close"])
        else:
            # nearest
            new_close = float(new_df["close"].iloc[0])
        # Spec text had old/new inverted; correct back-adjustment stitches earlier
        # prices onto the later contract: ratio = new_close / old_close.
        if old_close == 0:
            ratio = 1.0
        else:
            ratio = new_close / old_close
        cumulative *= ratio
        adj = old_df.copy()
        for col in ("open", "high", "low", "close"):
            adj[col] = adj[col] * cumulative
        adjusted.insert(0, adj)
        logger.debug(
            "roll adjust i={} ratio={:.6f} cumulative={:.6f}", i, ratio, cumulative
        )

    continuous = pd.concat(adjusted).sort_index()
    continuous = continuous[~continuous.index.duplicated(keep="last")]
    validate_ohlc_df(continuous)
    return continuous


def list_front_contracts(root: str, start: date, end: date) -> list[str]:
    """List unique front-month contracts covering [start, end]."""
    rule = get_roll_rule(root)
    segs = _contract_sequence(root, start, end, rule)
    return [s[0] for s in segs]
