# modes/chat_mode.py
import streamlit as st
from utils import init_history, generate_dummy_response
from config import TAB_LABELS

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            key = f"history_{label.replace(' ', '_').lower()}"
            init_history(key)
            history = st.session_state[key]

            # 1) input first so it updates immediately
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{key}")
            if prompt:
                history.append({"role": "user", "content": prompt})
                reply = generate_dummy_response(prompt)
                history.append({"role": "assistant", "content": reply})

            # 2) old messages in expander
            older = history[:-2]
            with st.expander("📜 Previous Messages", expanded=False):
                if not older:
                    st.info("No previous messages.")
                else:
                    for msg in older:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

            # 3) only latest exchange
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
