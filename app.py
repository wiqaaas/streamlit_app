# app.py
import streamlit as st
from modes.chat_mode   import run_chat_mode
from modes.generate_mode import run_generate_mode
from modes.filter_mode import run_filter_mode

st.set_page_config(page_title="Chat / Generate / Filter Demo", layout="wide")
st.title("Mode Selector")

# initialize histories for chat tabs
from utils import init_history
from config import TAB_LABELS
for lbl in TAB_LABELS:
    init_history(f"history_{lbl.replace(' ', '_').lower()}")

# Mode selection
if "mode" not in st.session_state:
    st.session_state.mode = None

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Chat"):
        st.session_state.mode = "chat"
with c2:
    if st.button("Generate"):
        st.session_state.mode = "generate"
with c3:
    if st.button("Filter"):
        st.session_state.mode = "filter"

st.markdown("---")

# Dispatch
mode = st.session_state.mode
if mode == "chat":
    run_chat_mode()
elif mode == "generate":
    run_generate_mode()
elif mode == "filter":
    run_filter_mode()
else:
    st.info("Select one of the modes above: **Chat**, **Generate** or **Filter**.")
