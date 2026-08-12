"""Full sheet generation integration tests against ES fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from PIL import Image

from levelsheet.config.loader import load_config
from levelsheet.render.compose import render_sheet
from levelsheet.render.export_pdf import export_pdf
from levelsheet.render.export_png import export_png
from levelsheet.render.sheet_data import build_sheet_data
from levelsheet.render.theme import Theme


def _load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    daily = pd.read_csv("tests/fixtures/ES_sample.csv", parse_dates=["date"]).set_index("date")
    weekly = pd.read_csv("tests/fixtures/ES_weekly_sample.csv", parse_dates=["date"]).set_index(
        "date"
    )
    monthly = pd.read_csv("tests/fixtures/ES_monthly_sample.csv", parse_dates=["date"]).set_index(
        "date"
    )
    for df in (daily, weekly, monthly):
        df.index = pd.DatetimeIndex(df.index).normalize()
        if "volume" in df.columns:
            df["volume"] = df["volume"].astype("Int64")
    return daily, weekly, monthly


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def test_full_sheet_generation(tmp_path: Path) -> None:
    daily, weekly, monthly = _load_frames()
    cfg = load_config()
    as_of = daily.index[-1].date()
    data = build_sheet_data("ES", as_of, daily, weekly, monthly, cfg)
    expected = json.loads(Path("tests/fixtures/expected_values.json").read_text())["ES_sample"]
    assert data.daily_pivots is not None
    assert abs(data.daily_pivots.p - expected["last_classic_pivot_p"]) < 1e-6
    assert data.ma_bias[200] == expected["ma200_bias"]

    fig = render_sheet(data, Theme.from_config(cfg.theme))
    pdf = tmp_path / "ES.pdf"
    png = tmp_path / "ES.png"
    export_pdf(fig, pdf)
    export_png(fig, png)
    assert pdf.stat().st_size > 50_000
    assert png.stat().st_size > 50_000
    im = Image.open(png)
    assert im.size == (5100, 3300)

    # Spot-check header background pixel matches theme.header_bg
    px = im.getpixel((120, 110))[:3]
    expected_bg = _hex_to_rgb(cfg.theme.header_bg)
    assert all(abs(px[i] - expected_bg[i]) <= 5 for i in range(3)), (px, expected_bg)


def test_theme_bullish_override_changes_pixels(tmp_path: Path) -> None:
    daily, weekly, monthly = _load_frames()
    base_cfg = load_config()
    as_of = daily.index[-1].date()

    # Render with default bullish
    data = build_sheet_data("ES", as_of, daily, weekly, monthly, base_cfg)
    fig1 = render_sheet(data, Theme.from_config(base_cfg.theme))
    png1 = tmp_path / "default.png"
    export_png(fig1, png1)

    # Override bullish to pure red-ish unique color
    overridden = base_cfg.model_copy(deep=True)
    overridden.theme.bullish = "#FF00AA"
    overridden.theme.bullish_fill_light = "#FF00AA"
    data2 = build_sheet_data("ES", as_of, daily, weekly, monthly, overridden)
    fig2 = render_sheet(data2, Theme.from_config(overridden.theme))
    png2 = tmp_path / "overridden.png"
    export_png(fig2, png2)

    im1 = Image.open(png1).convert("RGB")
    im2 = Image.open(png2).convert("RGB")
    # Count pixels close to #FF00AA in overridden image vs default
    target = (255, 0, 170)

    def count_near(im: Image.Image, color: tuple[int, int, int], tol: int = 20) -> int:
        w, h = im.size
        # subsample for speed
        count = 0
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                p = im.getpixel((x, y))
                if (
                    abs(p[0] - color[0]) <= tol
                    and abs(p[1] - color[1]) <= tol
                    and abs(p[2] - color[2]) <= tol
                ):
                    count += 1
        return count

    c1 = count_near(im1, target)
    c2 = count_near(im2, target)
    assert c2 > c1
    assert c2 > 100
