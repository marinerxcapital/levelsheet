"""Provider chain factory."""

from __future__ import annotations

from levelsheet.config.schema import LevelSheetConfig
from levelsheet.data.providers.base import DataProvider
from levelsheet.data.providers.ib_provider import IBProvider
from levelsheet.data.providers.polygon_provider import PolygonProvider
from levelsheet.data.providers.yfinance_provider import YFinanceProvider


def get_provider_chain(config: LevelSheetConfig) -> list[DataProvider]:
    """Return ordered available provider chain: Polygon → YFinance → IB."""
    candidates: list[DataProvider] = [
        PolygonProvider(api_key_env=config.data.providers.polygon_api_key_env),
        YFinanceProvider(),
        IBProvider(enabled_env=config.data.providers.ib_enabled_env),
    ]
    return [p for p in candidates if p.is_available()]
