# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st

from config import TAB_LABELS, FILENAME_MAP
import ai_client
from utils import init_history

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # 1) Load DataFrame from disk
            if label not in FILENAME_MAP:
                st.error(f"No filename mapped for tab “{label}”.")
                continue

            fname = FILENAME_MAP[label]
            file_path = os.path.join(DATA_DIR, fname)
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                st.error(f"Failed to load `{fname}`: {e}")
                continue

            # 2) Show the full DataFrame at the top
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Chat input
            history_key = f"history_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            prompt = st.chat_input(f"Type a message about this data…", key=history_key)

            if prompt:
                # record user message
                st.session_state[history_key].append({"role": "user", "content": prompt})

                # 4) Retrieve best-matching row via Qdrant through ai_client
                best_row = ai_client.get_best_matching_row(label, prompt)

                if not best_row.empty:
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                else:
                    st.info("No matching row found.")

                # record assistant note
                note = f"Displayed best match for “{prompt}”" if not best_row.empty else "No match found"
                st.session_state[history_key].append({
                    "role": "assistant",
                    "content": note
                })
