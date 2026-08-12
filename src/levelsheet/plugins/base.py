"""Plugin base protocol. Implemented in Phase 6."""

from __future__ import annotations

from typing import Protocol

from levelsheet.models.schemas import SheetData


class LevelSheetPlugin(Protocol):
    """Plugin that can enrich SheetData before render."""

    name: str

    def apply(self, data: SheetData) -> SheetData:
        """Transform or enrich sheet data."""
        ...
