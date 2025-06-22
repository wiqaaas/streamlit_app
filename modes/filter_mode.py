# modes/filter_mode.py
import streamlit as st
import pandas as pd
from config import TAB_LABELS

def run_filter_mode():
    st.header("🔍 Filter Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            hist_key = f"history_{label.replace(' ', '_').lower()}"
            history = st.session_state.get(hist_key, [])

            # 1) Load and display the dummy_data.xlsx
            try:
                df = pd.read_excel("dummy_data.xlsx")
                st.subheader(f"📊 Data for {label}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Failed to load dummy_data.xlsx: {e}")
                continue

            # 2) Keyword filter input
            kw = st.text_input(
                f"Keyword to filter in **{label}** history:",
                key=f"filter_kw_{hist_key}"
            )

            # 3) If no keyword entered, skip filtering history
            if not kw:
                st.info("Enter a keyword above to filter your stored chat messages.")
                continue

            # 4) Filter chat history messages
            matches = [
                msg for msg in history
                if kw.lower() in msg["content"].lower()
            ]

            # 5) Display filtered chat messages
            st.subheader(f"💬 Filtered Messages for {label}")
            if matches:
                for msg in matches:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            else:
                st.info(f"No messages in **{label}** matching “{kw}”.")
