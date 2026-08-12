"""Provider chain factory. Implemented in Phase 2."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from levelsheet.config.schema import LevelSheetConfig
    from levelsheet.data.providers.base import DataProvider


def get_provider_chain(config: "LevelSheetConfig") -> list["DataProvider"]:
    """Return ordered available provider chain. Stub — Phase 2."""
    raise NotImplementedError("Phase 2")
