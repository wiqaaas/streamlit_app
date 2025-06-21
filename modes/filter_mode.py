# modes/filter_mode.py
import streamlit as st
from config import TAB_LABELS

def run_filter_mode():
    st.header("🔍 Filter Mode")
    tab_choice = st.selectbox("Select tab to search:", ["All"] + TAB_LABELS, key="filter_tab")
    kw = st.text_input("Keyword to filter by:", key="filter_kw")

    if st.button("Apply Filter", key="filter_button"):
        results = []
        target_tabs = TAB_LABELS if tab_choice == "All" else [tab_choice]
        for lbl in target_tabs:
            hist = st.session_state.get(f"history_{lbl.replace(' ', '_').lower()}", [])
            for msg in hist:
                if kw.lower() in msg["content"].lower():
                    results.append((lbl, msg["role"], msg["content"]))

        if results:
            for lbl, role, content in results:
                st.markdown(f"**{lbl}** — *{role}*")
                st.write(content)
                st.markdown("---")
        else:
            st.info("No matching messages found.")
