# modes/filter_mode.py
import streamlit as st
from config import TAB_LABELS

def run_filter_mode():
    st.header("🔍 Filter Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            hist_key = f"history_{label.replace(' ', '_').lower()}"
            history = st.session_state.get(hist_key, [])

            kw = st.text_input(
                f"Keyword to filter in **{label}**:", 
                key=f"filter_kw_{hist_key}"
            )

            if not kw:
                st.info("Enter a keyword above to filter messages.")
                continue

            # find and display matches
            matches = [
                msg for msg in history
                if kw.lower() in msg["content"].lower()
            ]

            if matches:
                for msg in matches:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            else:
                st.info(f"No messages in **{label}** matching “{kw}”.")
