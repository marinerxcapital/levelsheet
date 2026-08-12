"""Classic, Camarilla, and Woodie floor pivot calculations."""

from __future__ import annotations

from typing import Optional

from loguru import logger
from pydantic import BaseModel


class PivotSet(BaseModel):
    """Pivot levels container supporting classic/camarilla/woodie subsets."""

    p: float
    r1: float
    r2: float
    s1: float
    s2: float
    r3: Optional[float] = None
    s3: Optional[float] = None
    r4: Optional[float] = None
    s4: Optional[float] = None


def classic_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute classic floor pivots.

    Formulas:
        P  = (H + L + C) / 3
        R1 = 2P - L;  S1 = 2P - H
        R2 = P + (H - L);  S2 = P - (H - L)
        R3 = H + 2(P - L);  S3 = L - 2(H - P)
    """
    p = (high + low + close) / 3
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2 * (p - low)
    s3 = low - 2 * (high - p)
    result = PivotSet(p=p, r1=r1, r2=r2, r3=r3, s1=s1, s2=s2, s3=s3)
    logger.debug("classic_pivots(high={}, low={}, close={}) -> {}", high, low, close, result)
    return result


def camarilla_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute Camarilla pivots.

    Formulas:
        rng = H - L
        R4 = C + rng * 1.1 / 2 … R1 = C + rng * 1.1 / 12
        S1..S4 mirror below close; P = close.
    """
    rng = high - low
    r4 = close + rng * 1.1 / 2
    r3 = close + rng * 1.1 / 4
    r2 = close + rng * 1.1 / 6
    r1 = close + rng * 1.1 / 12
    s1 = close - rng * 1.1 / 12
    s2 = close - rng * 1.1 / 6
    s3 = close - rng * 1.1 / 4
    s4 = close - rng * 1.1 / 2
    result = PivotSet(p=close, r1=r1, r2=r2, r3=r3, r4=r4, s1=s1, s2=s2, s3=s3, s4=s4)
    logger.debug("camarilla_pivots(high={}, low={}, close={}) -> {}", high, low, close, result)
    return result


def woodie_pivots(high: float, low: float, close: float) -> PivotSet:
    """Compute Woodie pivots.

    Formulas:
        P = (H + L + 2C) / 4
        R1 = 2P - L; S1 = 2P - H
        R2 = P + (H - L); S2 = P - (H - L)
    """
    p = (high + low + 2 * close) / 4
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    result = PivotSet(p=p, r1=r1, r2=r2, s1=s1, s2=s2)
    logger.debug("woodie_pivots(high={}, low={}, close={}) -> {}", high, low, close, result)
    return result
