# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st

from config import TAB_LABELS, FILENAME_MAP
import ai_client
from utils import init_history, generate_dummy_response

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # --- 1) Load DataFrame from disk ---
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

            # --- 2) Compute (or fetch cached) embeddings for each row ---
            row_embeds = ai_client.compute_row_embeddings(df)

            # --- 3) Show the full DataFrame at the top ---
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # --- 4) Chat input ---
            history_key = f"history_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            prompt = st.chat_input(f"Type a message about this data…", key=history_key)

            if prompt:
                # record user message (optional chat history)
                st.session_state[history_key].append({"role": "user", "content": prompt})

                # --- 5) Find and display the single best-matching row ---
                prompt_emb = ai_client.embed_text(prompt)
                best_idx = ai_client.find_best_row_index(row_embeds, prompt_emb)

                if best_idx is not None:
                    best_row = df.loc[[best_idx]]
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                else:
                    st.info("No matching row found.")

                # optional: append assistant note to history
                st.session_state[history_key].append({
                    "role": "assistant",
                    "content": f"Displayed row {best_idx}" if best_idx is not None else "No match"
                })
