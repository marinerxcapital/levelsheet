"""Compose the full levels sheet figure from SheetData."""

from __future__ import annotations

import seaborn as sns
from matplotlib import gridspec
from matplotlib.figure import Figure
from matplotlib.figure import Figure as FigureType

from levelsheet.errors import RenderError
from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import register_custom_fonts
from levelsheet.render.layout import DPI, FIGSIZE, SHEET_LAYOUT
from levelsheet.render.panels import (
    atr_nr7,
    autotrade_panel,
    bias_panel,
    center_ohlc_ma,
    daily_fib_extreme,
    daily_pivots,
    elliott_panel,
    footer,
    header,
    long_term_fib,
    mini_candlestick,
    projected_ma_panel,
    warnings_panel,
    weekly_monthly,
)
from levelsheet.render.theme import Theme


def _subplot(fig: Figure, gs: gridspec.GridSpec, name: str):  # type: ignore[no-untyped-def]
    region = SHEET_LAYOUT[name]
    return fig.add_subplot(
        gs[region.row_start : region.row_end, region.col_start : region.col_end]
    )


def render_sheet(data: SheetData, theme: Theme | None = None) -> FigureType:
    """Render a complete levels sheet figure.

    Args:
        data: Fully computed sheet payload.
        theme: Optional theme; defaults to Theme().

    Returns:
        matplotlib Figure at 17×11, 300 DPI.
    """
    theme = theme or Theme()
    try:
        register_custom_fonts()
        sns.set_theme(style="white", font_scale=1.0)
        fig = Figure(figsize=FIGSIZE, dpi=DPI, facecolor="#FFFFFF")
        gs = gridspec.GridSpec(
            nrows=80,
            ncols=120,
            figure=fig,
            left=0.02,
            right=0.98,
            top=0.97,
            bottom=0.03,
            wspace=0.0,
            hspace=0.0,
        )
        header.draw(_subplot(fig, gs, "header"), data, theme)
        daily_pivots.draw(_subplot(fig, gs, "daily_pivots"), data, theme)
        center_ohlc_ma.draw(_subplot(fig, gs, "center_ohlc_ma"), data, theme)
        mini_candlestick.draw(_subplot(fig, gs, "mini_candlestick"), data, theme)
        weekly_monthly.draw_weekly(_subplot(fig, gs, "weekly_panel"), data, theme)
        weekly_monthly.draw_monthly(_subplot(fig, gs, "monthly_panel"), data, theme)
        atr_nr7.draw(_subplot(fig, gs, "atr_nr7_panel"), data, theme)
        atr_nr7.draw_hilo(_subplot(fig, gs, "hilo_7_20_panel"), data, theme)
        long_term_fib.draw(_subplot(fig, gs, "long_term_fib"), data, theme)
        daily_fib_extreme.draw(_subplot(fig, gs, "daily_fib_extreme"), data, theme)
        bias_panel.draw(_subplot(fig, gs, "bias_panel"), data, theme)
        autotrade_panel.draw(_subplot(fig, gs, "autotrade_panel"), data, theme)
        elliott_panel.draw(_subplot(fig, gs, "elliott_panel"), data, theme)
        projected_ma_panel.draw(_subplot(fig, gs, "projected_ma_panel"), data, theme)
        warnings_panel.draw(_subplot(fig, gs, "warnings_panel"), data, theme)
        footer.draw(_subplot(fig, gs, "footer"), data, theme)
        return fig
    except Exception as exc:  # noqa: BLE001
        raise RenderError(f"Failed to render sheet for {data.root}") from exc
