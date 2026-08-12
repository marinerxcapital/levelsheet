"""LevelSheet Streamlit GUI — phone + desktop friendly."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from levelsheet.config.loader import load_config
from levelsheet.pipeline import build_book_bytes, build_sheet_bytes


def _configured_password() -> str:
    env = os.environ.get("LEVELSHEET_PASSWORD", "").strip()
    if env:
        return env
    try:
        return str(st.secrets.get("LEVELSHEET_PASSWORD", "")).strip()
    except Exception:
        return ""


def _gate() -> bool:
    """Optional shared password for public hosts (phone / desktop)."""
    expected = _configured_password()
    if not expected:
        return True
    if st.session_state.get("ls_authed"):
        return True
    st.title("LevelSheet")
    st.caption("Enter the shared password to open sheets on this device.")
    entered = st.text_input("Password", type="password")
    if st.button("Unlock", type="primary", use_container_width=True):
        if entered == expected:
            st.session_state["ls_authed"] = True
            st.rerun()
        st.error("Wrong password.")
    return False


config = load_config()

_logo_candidates = (
    Path(__file__).resolve().parents[3] / "assets" / "logo" / "logo.png",
    Path.cwd() / "assets" / "logo" / "logo.png",
)
_logo = next((p for p in _logo_candidates if p.is_file()), None)
st.set_page_config(
    page_title="LevelSheet",
    page_icon=str(_logo) if _logo is not None else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

if not _gate():
    st.stop()

st.title("LevelSheet")
st.caption("Futures daily levels — generate on phone or desktop, download PDF/PNG.")

defaults = config.symbols.default_list

with st.sidebar:
    st.subheader("Sheet")
    chosen = st.selectbox("Symbol", defaults, index=0)
    custom = st.text_input("Custom root (optional)", placeholder="overrides dropdown")
    symbol = custom.strip().upper() or chosen
    the_date = st.date_input("Date", value=date.today())
    pivot_method = st.radio(
        "Pivot method",
        ["classic", "camarilla", "woodie"],
        index=0,
        horizontal=True,
    )
    generate = st.button("Generate Sheet", type="primary", use_container_width=True)

tab_single, tab_batch = st.tabs(["Single Sheet", "Full Book"])

with tab_single:
    if generate:
        with st.spinner(f"Generating {symbol} · {the_date}…"):
            fig, pdf_bytes, png_bytes = build_sheet_bytes(
                symbol, the_date, config, pivot_method=str(pivot_method)
            )
            plt.close(fig)
        st.session_state["last_sheet"] = {
            "symbol": symbol,
            "date": the_date.isoformat(),
            "pdf": pdf_bytes,
            "png": png_bytes,
        }

    sheet = st.session_state.get("last_sheet")
    if sheet:
        st.markdown(f"**{sheet['symbol']}** · {sheet['date']}")
        # PNG preview is far more reliable on mobile Safari than pyplot widgets
        st.image(sheet["png"], use_container_width=True)
        d1, d2 = st.columns(2)
        d1.download_button(
            "Download PDF",
            sheet["pdf"],
            file_name=f"{sheet['symbol']}_{sheet['date']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        d2.download_button(
            "Download PNG",
            sheet["png"],
            file_name=f"{sheet['symbol']}_{sheet['date']}.png",
            mime="image/png",
            use_container_width=True,
        )
        st.info(
            "iPhone tip: open the PNG download, then Share → **Add to Photos**, "
            "or Safari Share → **Add to Home Screen** for a one-tap LevelSheet icon."
        )
    else:
        st.write("Pick a symbol and tap **Generate Sheet**.")

with tab_batch:
    picked = st.multiselect("Symbols for book", defaults, default=defaults[:4])
    if st.button("Export Full Book", use_container_width=True):
        with st.spinner("Building multi-page book…"):
            book_pdf_bytes = build_book_bytes(list(picked), the_date, config)
        st.session_state["last_book"] = {
            "date": the_date.isoformat(),
            "pdf": book_pdf_bytes,
        }
    book = st.session_state.get("last_book")
    if book:
        st.download_button(
            "Download Book PDF",
            book["pdf"],
            file_name=f"book_{book['date']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
