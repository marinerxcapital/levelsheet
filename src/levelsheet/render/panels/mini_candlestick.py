"""Mini candlestick panel."""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from levelsheet.calc.warnings_flags import OHLCBar
from levelsheet.models.schemas import SheetData
from levelsheet.render.fonts import FONT_SIZES
from levelsheet.render.theme import Theme


def draw_single_candle(ax: Axes, ohlc: OHLCBar, theme: Theme) -> None:
    """Draw one normalized candlestick in axes fraction space."""
    rng = ohlc.high - ohlc.low
    pad = rng * 0.10 if rng > 0 else 1.0
    lo = ohlc.low - pad
    hi = ohlc.high + pad
    span = hi - lo if hi > lo else 1.0

    def norm(v: float) -> float:
        return (v - lo) / span

    body_color = theme.bullish if ohlc.close >= ohlc.open else theme.bearish
    ax.add_line(
        Line2D(
            [0.5, 0.5],
            [norm(ohlc.low), norm(ohlc.high)],
            transform=ax.transAxes,
            color=body_color,
            linewidth=1.5,
            clip_on=False,
        )
    )
    body_bottom = min(norm(ohlc.open), norm(ohlc.close))
    body_h = abs(norm(ohlc.close) - norm(ohlc.open))
    if body_h < 0.01:
        body_h = 0.01
    ax.add_patch(
        Rectangle(
            (0.3, body_bottom),
            0.4,
            body_h,
            transform=ax.transAxes,
            facecolor=body_color,
            edgecolor=theme.border,
            linewidth=theme.border_width_pt,
            clip_on=False,
        )
    )


def draw(ax: Axes, data: SheetData, theme: Theme) -> None:
    """Draw mini candlestick for today."""
    ax.axis("off")
    ax.text(
        0.5,
        0.98,
        "CANDLE",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=FONT_SIZES["panel_header"],
        fontweight="bold",
        color=theme.body_text,
        fontfamily=theme.font_family,
    )
    if data.today_bar is not None:
        # Draw into a sub-region
        draw_single_candle(ax, data.today_bar, theme)


def to_html(data: SheetData, theme: Theme) -> str:
    """HTML fragment for weasyprint fallback."""
    return "<div>Candle</div>"
