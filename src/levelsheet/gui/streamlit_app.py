"""LevelSheet Streamlit GUI. Fully wired in Phase 5."""

from __future__ import annotations

from datetime import date

import streamlit as st

from levelsheet.config.loader import load_config

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
        st.info("Sheet generation wires up in Phase 5.")
        st.write({"symbol": symbol, "date": str(the_date), "pivot_method": pivot_method})
with tab_batch:
    picked = st.multiselect("Symbols for book", default_symbols, default=default_symbols[:4])
    if st.button("Export Full Book"):
        st.info(f"Book export for {picked} wires up in Phase 5.")
