"""Plugin registry and sample plugins."""

from __future__ import annotations

from levelsheet.models.schemas import SheetData
from levelsheet.plugins.base import LevelSheetPlugin


class AnnotateRootPlugin:
    """Example plugin that stamps root into extras."""

    name = "annotate_root"

    def apply(self, data: SheetData) -> SheetData:
        extras = dict(data.extras)
        extras["annotated_root"] = data.root
        return data.model_copy(update={"extras": extras})


class PluginRegistry:
    """Register and apply enabled plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, LevelSheetPlugin] = {}

    def register(self, plugin: LevelSheetPlugin) -> None:
        """Register a plugin by name."""
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> LevelSheetPlugin | None:
        """Return plugin by name if registered."""
        return self._plugins.get(name)

    def apply_all(self, data: SheetData, enabled: list[str]) -> SheetData:
        """Apply enabled plugins in order."""
        for name in enabled:
            plugin = self._plugins.get(name)
            if plugin is not None:
                data = plugin.apply(data)
        return data


REGISTRY = PluginRegistry()
REGISTRY.register(AnnotateRootPlugin())
