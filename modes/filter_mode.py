# modes/filter_mode.py
import os
import streamlit as st
import pandas as pd
from config import TAB_LABELS
from utils import generate_dummy_response
from modes.generate_mode import (
    DEFAULT_MATCH_TEXT,
    DEFAULT_LESSON_TEXT,
    DEFAULT_COURSE_TEXT,
    DEFAULT_ARTICLE_TEXT,
)

# Map each tab to its Excel filename
FILENAME_MAP = {
    "Upcoming Match": "df_schedule.xlsx",
    "Lesson":         "df_lessons.xlsx",
    "Course":         "df_courses.xlsx",
    "Article":        "df_article_schedule.xlsx",
}

# Compute paths
BASE_DIR     = os.path.dirname(__file__)                     
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")            

def run_filter_mode():
    st.header("🔍 Filter & Generate Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            st.subheader(f"📊 {label} Data")

            # --- 1) Load DataFrame ---
            filename = FILENAME_MAP[label]
            path = os.path.join(DATA_DIR, filename)
            try:
                df = pd.read_excel(path)
            except Exception as e:
                st.error(f"Failed to load `{filename}`: {e}")
                continue

            # --- 2) Exact-match filters ---
            st.markdown("**Filter by exact column values (leave blank to skip):**")
            filters = {}
            with st.expander("Show filters", expanded=False):
                for col in df.columns:
                    choices = [""] + sorted(df[col].dropna().astype(str).unique())
                    filters[col] = st.selectbox(
                        label=col,
                        options=choices,
                        key=f"flt_{label}_{col}"
                    )

            df_filt = df.copy()
            for col, val in filters.items():
                if val != "":
                    df_filt = df_filt[df_filt[col].astype(str) == val]

            if df_filt.empty:
                st.warning("No rows match your filters.")
                continue

            # --- 3) Show filtered table with original indices ---
            st.dataframe(df_filt)

            # --- 4) Pick one original index to inspect ---
            idx = st.selectbox(
                "Select the exact row index to inspect:",
                options=list(df_filt.index),
                key=f"idx_{label}"
            )
            row = df_filt.loc[idx]
            # build the info string once
            row_info = "; ".join(f"{col}: {row[col]}" for col in df_filt.columns)

            st.markdown(f"**Selected Row {idx}:** {row_info}")
            st.markdown("---")

            # --- 5) Now inject the Generate-mode UI for this tab ---
            base = label.replace(" ", "_").lower()
            hist_key  = f"filter_gen_history_{base}"
            inp_key   = f"filter_gen_input_{base}"
            btn_key   = f"filter_gen_send_{base}"
            clr_key   = f"filter_gen_clear_{base}"

            # init history & clear flag
            if hist_key not in st.session_state:
                st.session_state[hist_key] = []
            if clr_key not in st.session_state:
                st.session_state[clr_key] = False

            # handle send button
            if st.button("Send", key=btn_key):
                msg = st.session_state.get(inp_key, "").strip()
                if msg:
                    st.session_state[hist_key].append(msg)
                    st.session_state[clr_key] = True
                else:
                    st.warning("Please enter a message to send.")

            # clear input if flagged
            if st.session_state[clr_key]:
                st.session_state[inp_key] = ""
                st.session_state[clr_key] = False

            # 5.1) show default copy for this tab
            if label == "Upcoming Match":
                st.markdown(DEFAULT_MATCH_TEXT)
            elif label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)
            elif label == "Course":
                st.markdown(DEFAULT_COURSE_TEXT)
            elif label == "Article":
                st.markdown(DEFAULT_ARTICLE_TEXT)

            # 5.2) show user’s generate-mode history
            history = st.session_state[hist_key]
            if history:
                st.markdown("**Your Inputs So Far:**")
                for entry in history:
                    st.write(f"- {entry}")
                st.markdown("---")

            # 5.3) finally, the text_input for new messages
            st.text_input(f"Type your message for “{label}”…", key=inp_key)
