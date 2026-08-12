"""Simplified Elliott Wave zigzag detection and Wave-5 projection."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
from loguru import logger
from pydantic import BaseModel, Field

from levelsheet.errors import InsufficientHistoryError


class ElliottProjection(BaseModel):
    """Elliott wave projection result."""

    waves: list[dict[str, Any]] = Field(default_factory=list)
    ext_ratio: float
    wave5_target: float
    extended_third: Optional[bool] = None


def detect_swings_zigzag(df: pd.DataFrame, threshold_pct: float = 3.0) -> pd.DataFrame:
    """Standard percentage zigzag swing detection.

    Confirms a High when price reverses from the running max by >= threshold_pct;
    confirms a Low when price reverses from the running min by >= threshold_pct.
    The final unconfirmed running extreme is NOT added (no lookahead).
    Returns columns: [date, price, kind] with kind in {\"High\",\"Low\"}, strictly alternating.
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "price", "kind"])

    closes = df["close"].astype(float)
    highs = df["high"].astype(float)
    lows = df["low"].astype(float)
    index = df.index

    last_extreme_price = float(closes.iloc[0])
    last_extreme_idx = 0
    direction: Optional[str] = None

    running_max = float(highs.iloc[0])
    running_max_idx = 0
    running_min = float(lows.iloc[0])
    running_min_idx = 0

    swings: list[dict[str, Any]] = []

    for i in range(1, len(df)):
        if direction in (None, "up"):
            if highs.iloc[i] >= running_max:
                running_max = float(highs.iloc[i])
                running_max_idx = i
            if lows.iloc[i] <= running_max * (1 - threshold_pct / 100):
                swings.append(
                    {
                        "date": index[running_max_idx],
                        "price": running_max,
                        "kind": "High",
                    }
                )
                direction = "down"
                last_extreme_price = running_max
                last_extreme_idx = running_max_idx
                running_min = float(lows.iloc[i])
                running_min_idx = i
                continue

        if direction in (None, "down"):
            if lows.iloc[i] <= running_min:
                running_min = float(lows.iloc[i])
                running_min_idx = i
            if highs.iloc[i] >= running_min * (1 + threshold_pct / 100):
                swings.append(
                    {
                        "date": index[running_min_idx],
                        "price": running_min,
                        "kind": "Low",
                    }
                )
                direction = "up"
                last_extreme_price = running_min
                last_extreme_idx = running_min_idx
                running_max = float(highs.iloc[i])
                running_max_idx = i

    # Ensure strictly alternating by dropping consecutive same-kind (keep more extreme)
    cleaned: list[dict[str, Any]] = []
    for s in swings:
        if cleaned and cleaned[-1]["kind"] == s["kind"]:
            if s["kind"] == "High" and s["price"] >= cleaned[-1]["price"]:
                cleaned[-1] = s
            elif s["kind"] == "Low" and s["price"] <= cleaned[-1]["price"]:
                cleaned[-1] = s
        else:
            cleaned.append(s)

    result = pd.DataFrame(cleaned, columns=["date", "price", "kind"])
    logger.debug(
        "detect_swings_zigzag(threshold_pct={}, n={}) -> {} swings (last_extreme={}@{})",
        threshold_pct,
        len(df),
        len(result),
        last_extreme_price,
        last_extreme_idx,
    )
    return result


def elliott_wave_projection(swings: pd.DataFrame) -> ElliottProjection:
    """Project Wave 5 target from last 6 swing points (Wave 0–5).

    Requires >= 6 points; raises InsufficientHistoryError otherwise.
    """
    if len(swings) < 6:
        raise InsufficientHistoryError(
            f"elliott_wave_projection requires >= 6 swing points, got {len(swings)}"
        )
    tail = swings.tail(6).reset_index(drop=True)
    prices = [float(p) for p in tail["price"].tolist()]
    wave1_len = abs(prices[1] - prices[0])
    wave3_len = abs(prices[3] - prices[2])
    wave4_end = prices[4]
    extended_third = wave3_len > wave1_len * 1.618
    ext_ratio = 2.618 if extended_third else 1.618
    direction_sign = 1 if prices[1] > prices[0] else -1
    wave5_target = round(wave4_end + direction_sign * wave1_len * ext_ratio, 2)
    waves = [
        {"date": str(row["date"]), "price": float(row["price"]), "kind": str(row["kind"])}
        for _, row in tail.iterrows()
    ]
    result = ElliottProjection(
        waves=waves,
        ext_ratio=ext_ratio,
        wave5_target=wave5_target,
        extended_third=extended_third,
    )
    logger.debug("elliott_wave_projection -> {}", result)
    return result
