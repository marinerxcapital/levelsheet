"""Application error hierarchy for LevelSheet.

All public functions in calc/, data/, and render/ raise one of these
so the CLI top-level handler can catch LevelSheetError uniformly.
"""


class LevelSheetError(Exception):
    """Base class for all application errors."""


class ConfigError(LevelSheetError):
    """Raised on invalid or missing configuration."""


class ProviderUnavailableError(LevelSheetError):
    """Raised when a data provider cannot be used (missing key, missing package, network down)."""


class DataValidationError(LevelSheetError):
    """Raised when fetched/cached OHLC data fails schema validation."""


class InsufficientHistoryError(LevelSheetError):
    """Raised when a calculation needs more bars than are available."""


class RollCalendarError(LevelSheetError):
    """Raised when a root has no roll calendar entry and none was provided via config override."""


class RenderError(LevelSheetError):
    """Raised on any matplotlib/reportlab/weasyprint failure during sheet composition."""


class ExportError(LevelSheetError):
    """Raised when PDF/PNG write fails (disk, permissions, invalid path)."""


class CacheError(LevelSheetError):
    """Raised on cache read/write corruption; handler should log + fall through to network fetch."""
