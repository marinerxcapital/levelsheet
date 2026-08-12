"""LevelSheet Streamlit GUI."""

from __future__ import annotations

from datetime import date

import streamlit as st

from levelsheet.config.loader import load_config
from levelsheet.pipeline import build_book_bytes, build_sheet_bytes

config = load_config()

st.set_page_config(page_title="LevelSheet", layout="wide")
with st.sidebar:
    default_symbols = config.symbols.default_list
    chosen = st.selectbox("Symbol (or type any root below)", default_symbols)
    custom = st.text_input("Custom root (overrides dropdown)", "")
    symbol = custom.strip().upper() or chosen
    the_date = st.date_input("Date", value=date.today())
    pivot_method = st.radio("Pivot method", ["classic", "camarilla", "woodie"], index=0)
    generate = st.button("Generate Sheet", type="primary")

tab_single, tab_batch = st.tabs(["Single Sheet", "Full Book"])
with tab_single:
    if generate:
        with st.spinner(f"Generating {symbol} sheet for {the_date}..."):
            fig, pdf_bytes, png_bytes = build_sheet_bytes(
                symbol, the_date, config, pivot_method=str(pivot_method)
            )
        st.pyplot(fig)
        col1, col2 = st.columns(2)
        col1.download_button(
            "Download PDF",
            pdf_bytes,
            file_name=f"{symbol}_{the_date}.pdf",
            mime="application/pdf",
        )
        col2.download_button(
            "Download PNG",
            png_bytes,
            file_name=f"{symbol}_{the_date}.png",
            mime="image/png",
        )
with tab_batch:
    picked = st.multiselect("Symbols for book", default_symbols, default=default_symbols[:4])
    if st.button("Export Full Book"):
        with st.spinner("Building multi-page book..."):
            book_pdf_bytes = build_book_bytes(list(picked), the_date, config)
        st.download_button(
            "Download Book PDF",
            book_pdf_bytes,
            file_name=f"book_{the_date}.pdf",
            mime="application/pdf",
        )
