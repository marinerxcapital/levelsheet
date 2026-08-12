"""PNG export."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from levelsheet.errors import ExportError


def export_png(fig: Figure, path: Path) -> None:
    """Save figure as 300 DPI PNG; require file size > 50KB."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, format="png", facecolor=fig.get_facecolor())
    except Exception as exc:  # noqa: BLE001
        raise ExportError(f"Failed to write PNG {path}") from exc
    if not path.exists() or path.stat().st_size <= 50_000:
        raise ExportError(f"PNG sanity check failed for {path} (size too small)")
