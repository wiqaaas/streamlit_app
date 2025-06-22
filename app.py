# app.py
import os
import streamlit as st
from utils import init_history
from config import TAB_LABELS
from modes.chat_mode import run_chat_mode
from modes.generate_mode import run_generate_mode
from modes.filter_mode import run_filter_mode

# --- Page config ---
st.set_page_config(
    page_title="Multipurpose Demo App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- App title & description ---
st.title("🤖 Multipurpose Streamlit App")

# --- Initialize chat histories ---
for lbl in TAB_LABELS:
    key = f"history_{lbl.replace(' ', '_').lower()}"
    init_history(key)

# --- Sidebar: select mode ---
mode = st.sidebar.radio(
    "Select a mode",
    ("💬 Chat", "⚙️ Generate", "🔍 Filter & Generate"),
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.write("Built by Waqas")

# --- Dispatch to the appropriate mode ---
if mode == "💬 Chat":
    run_chat_mode()

elif mode == "⚙️ Generate":
    run_generate_mode()

elif mode == "🔍 Filter & Generate":
    run_filter_mode()
