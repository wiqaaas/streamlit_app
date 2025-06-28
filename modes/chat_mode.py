# modes/chat_mode.py

import streamlit as st
from config import TAB_LABELS
import ai_client  # our new client with all the AI logic in it

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # 1) Load DataFrame & row embeddings once (cached in ai_client)
            df, _ = ai_client.load_data_and_embeddings(label)

            # 2) Show the full DataFrame at the very top
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Chat box
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{label}")

            if prompt:
                # 4) Fetch the single best-matching row
                best_row = ai_client.get_best_matching_row(label, prompt)

                # 5) Display it immediately below
                if not best_row.empty:
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                else:
                    st.info("No matching row found.")
