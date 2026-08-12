"""Pydantic v2 configuration schema for LevelSheet.

Full models implemented in Phase 6; stub placeholders for Phase 0.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SymbolsConfig(BaseModel):
    """Default symbol list and optional point-value overrides."""

    default_list: list[str] = ["ES", "NQ", "CL", "GC", "SI", "ZB", "6E", "RTY"]
    point_values: dict[str, float] = {}


class PivotsConfig(BaseModel):
    """Pivot calculation method selection."""

    method: Literal["classic", "camarilla", "woodie"] = "classic"
    show_camarilla: bool = False
    show_woodie: bool = False


class MovingAveragesConfig(BaseModel):
    """Moving average lengths and type."""

    lengths: list[int] = [5, 13, 50, 100, 150, 200]
    type: Literal["sma", "ema"] = "sma"


class FibonacciConfig(BaseModel):
    """Fibonacci retracement/extension ratios and swing threshold."""

    retracement_ratios: list[float] = [0.0, 0.236, 0.382, 0.5, 0.618, 0.764, 1.0]
    extension_ratios: list[float] = [1.272, 1.618, 2.0, 2.618]
    long_term_swing_threshold_pct: float = 5.0


class ElliottWaveConfig(BaseModel):
    """Zigzag threshold for Elliott wave detection."""

    zigzag_threshold_pct: float = 3.0


class ATRConfig(BaseModel):
    """ATR length and method."""

    length: int = Field(14, gt=0)
    method: Literal["wilder"] = "wilder"


class AutoTradeConfig(BaseModel):
    """Auto-trade risk sizing multipliers and defaults."""

    stop_atr_mult: float = 1.0
    trail_atr_mult: float = 0.5
    target_atr_mult: float = 2.0
    frequency: str = "1/day"
    side: Literal["BOTH", "LONG", "SHORT"] = "BOTH"
    contracts: int = 1
    scale_out_pct: float = 50.0


class ExtremeMovesConfig(BaseModel):
    """Percentage moves for extreme-move targets."""

    percentages: list[float] = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]


class WarningsConfig(BaseModel):
    """Warning flag thresholds."""

    rth_gap_threshold_pct: float = 0.15
    close_proximity_pct: float = 25.0


class ThemeConfig(BaseModel):
    """Color theme hex codes and font family."""

    bullish: str = "#1B7A3D"
    bullish_fill_light: str = "#E9F6EC"
    bearish: str = "#B32020"
    bearish_fill_light: str = "#FBE9E9"
    key_level: str = "#F2C230"
    key_level_text: str = "#5A4300"
    open_settlement: str = "#ADD8E6"
    neutral: str = "#8C8C8C"
    header_bg: str = "#0B1F33"
    header_text: str = "#FFFFFF"
    border: str = "#333333"
    font_family: str = "DejaVu Sans"

    @field_validator("*")
    @classmethod
    def _validate_hex(cls, v: str, info: object) -> str:
        field_name = getattr(info, "field_name", "")
        if field_name in ("font_family",):
            return v
        if not (isinstance(v, str) and v.startswith("#") and len(v) in (4, 7)):
            raise ValueError(f"{field_name} must be a hex color, got {v!r}")
        return v


class BrandingConfig(BaseModel):
    """Company branding for header/footer."""

    company_name: str = "BPTC 26 LLC"
    footer_text: str = "For educational purposes only. Not financial advice."
    logo_path: str = "assets/logo/logo.png"


class CacheConfig(BaseModel):
    """Cache backend and freshness policy."""

    backend: Literal["parquet", "sqlite"] = "parquet"
    dir: str = "cache"
    max_staleness_hours: int = 18


class ProvidersConfig(BaseModel):
    """Environment variable names for provider credentials."""

    polygon_api_key_env: str = "POLYGON_API_KEY"
    ib_enabled_env: str = "IB_ENABLED"


class DataConfig(BaseModel):
    """Data layer configuration."""

    cache: CacheConfig = CacheConfig()
    providers: ProvidersConfig = ProvidersConfig()


class RenderConfig(BaseModel):
    """Render engine and output settings."""

    engine: Literal["matplotlib", "weasyprint"] = "matplotlib"
    dpi: int = 300
    page_size: Literal["letter_landscape"] = "letter_landscape"


class PluginsConfig(BaseModel):
    """Enabled plugin names."""

    enabled: list[str] = []


class LevelSheetConfig(BaseModel):
    """Root LevelSheet configuration model."""

    symbols: SymbolsConfig = SymbolsConfig()
    pivots: PivotsConfig = PivotsConfig()
    moving_averages: MovingAveragesConfig = MovingAveragesConfig()
    fibonacci: FibonacciConfig = FibonacciConfig()
    elliott_wave: ElliottWaveConfig = ElliottWaveConfig()
    atr: ATRConfig = ATRConfig()
    autotrade: AutoTradeConfig = AutoTradeConfig()
    extreme_moves: ExtremeMovesConfig = ExtremeMovesConfig()
    warnings: WarningsConfig = WarningsConfig()
    theme: ThemeConfig = ThemeConfig()
    branding: BrandingConfig = BrandingConfig()
    data: DataConfig = DataConfig()
    render: RenderConfig = RenderConfig()
    plugins: PluginsConfig = PluginsConfig()
