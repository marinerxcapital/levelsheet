"""Plugin registry. Implemented in Phase 6."""

from __future__ import annotations

from levelsheet.models.schemas import SheetData
from levelsheet.plugins.base import LevelSheetPlugin


class PluginRegistry:
    """Register and apply enabled plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, LevelSheetPlugin] = {}

    def register(self, plugin: LevelSheetPlugin) -> None:
        """Register a plugin by name."""
        self._plugins[plugin.name] = plugin

    def apply_all(self, data: SheetData, enabled: list[str]) -> SheetData:
        """Apply enabled plugins in order. Stub — Phase 6."""
        for name in enabled:
            plugin = self._plugins.get(name)
            if plugin is not None:
                data = plugin.apply(data)
        return data


REGISTRY = PluginRegistry()
