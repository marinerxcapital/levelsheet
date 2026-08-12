"""matplotlib Agg backend must be set before any other matplotlib import."""

import matplotlib

matplotlib.use("Agg")

from levelsheet.render.compose import render_sheet
from levelsheet.render.sheet_data import build_sheet_data

__all__ = ["render_sheet", "build_sheet_data"]
