# app.py
import os
import streamlit as st
from utils import init_history
from config import TAB_LABELS
from modes.chat_mode import run_chat_mode
from modes.filter_mode import run_filter_mode
from modes.centralized_mode import run_centralized_mode

# --- Page config ---
st.set_page_config(
    # page_title="Multipurpose Demo App",
    # page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- App title & description ---
# st.title("🤖 Multipurpose Streamlit App")

# --- Initialize chat histories ---
for lbl in TAB_LABELS:
    key = f"history_{lbl.replace(' ', '_').lower()}"
    init_history(key)

# --- Sidebar: select mode ---
mode = st.sidebar.radio(
    "Select a mode",
    ("💬 Chat", 
    "⚙️ Centralized Generation", 
    "🔍 Filter & Generate"),
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.write("Built by MySportsAnalysis Ltd")

# --- Dispatch to the appropriate mode ---
if mode == "💬 Chat":
    run_chat_mode()

elif mode == "⚙️ Centralized Generation":
    run_centralized_mode()

elif mode == "🔍 Filter & Generate":
    run_filter_mode()
