# modes/chat_mode.py
import os
import pandas as pd
import streamlit as st
from utils import init_history, generate_dummy_response
from config import TAB_LABELS, FILENAME_MAP, DATA_DIR

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            key = f"history_{label.replace(' ', '_').lower()}"
            init_history(key)
            history = st.session_state[key]

            # 1) Chat input first so it updates immediately
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{key}")
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

            # 3) Show the latest exchange inline
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # 4) Load & display the full DataFrame for this tab
            fname = FILENAME_MAP.get(label)
            if fname:
                file_path = os.path.join(DATA_DIR, fname)
                try:
                    df = pd.read_excel(file_path)
                    st.markdown(f"### 📊 `{fname}`")
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not load `{fname}`: {e}")
            else:
                st.warning(f"No filename mapped for tab `{label}`.")
