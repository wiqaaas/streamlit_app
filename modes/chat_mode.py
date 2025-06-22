# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st
from utils import init_history, generate_dummy_response
from config import TAB_LABELS, FILENAME_MAP

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

# Cache each Excel load so it only happens once per session
@st.cache_data
def load_dataframe(fname: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, fname)
    return pd.read_excel(path)

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            history_key = f"history_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            history = st.session_state[history_key]

            # 1) Capture new user input first
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{history_key}")
            if prompt:
                history.append({"role": "user", "content": prompt})
                reply = generate_dummy_response(prompt)
                history.append({"role": "assistant", "content": reply})

            # 2) Show older messages in an expander
            older = history[:-2]
            with st.expander("📜 Previous Messages", expanded=False):
                if not older:
                    st.info("No previous messages.")
                else:
                    for msg in older:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

            # 3) Show latest exchange inline
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # 4) Load & display the full DataFrame (cached)
            fname = FILENAME_MAP.get(label)
            if fname:
                try:
                    df = load_dataframe(fname)
                    st.markdown(f"### 📊 `{fname}`")
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not load `{fname}`: {e}")
            else:
                st.warning(f"No filename mapped for tab `{label}`.")
