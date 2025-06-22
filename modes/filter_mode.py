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

# Compute project & data directories
BASE_DIR     = os.path.dirname(__file__)                     
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")            

@st.cache_data(show_spinner=False)
def load_all_dataframes():
    """Load each Excel once per session."""
    dfs = {}
    for label, fname in FILENAME_MAP.items():
        path = os.path.join(DATA_DIR, fname)
        dfs[label] = pd.read_excel(path)
    return dfs

def run_filter_mode():
    st.header("🔍 Dynamic Filter & Generate Mode")

    # 1) Load all DataFrames (cached)
    dfs = load_all_dataframes()

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            st.subheader(f"📊 {label} Data")

            df = dfs.get(label)
            if df is None:
                st.error(f"No data for **{label}**.")
                continue

            # 2) Clear All Filters button
            if st.button("Clear All Filters", key=f"clear_filters_{label}"):
                for col in df.columns:
                    st.session_state[f"flt_{label}_{col}"] = ""
                st.experimental_rerun()

            # 3) Build and render interdependent filters
            st.markdown("**Filter by exact column values (select to narrow):**")
            filters = {}
            with st.expander("Show filters", expanded=False):
                for col in df.columns:
                    # Apply all other filters first to compute valid choices
                    temp = df.copy()
                    for other in df.columns:
                        if other == col:
                            continue
                        key_other = f"flt_{label}_{other}"
                        val_other = st.session_state.get(key_other, "")
                        if val_other:
                            temp = temp[temp[other].astype(str) == val_other]

                    # Gather unique options for this column
                    unique_vals = sorted(temp[col].dropna().astype(str).unique())
                    choices = [""] + unique_vals

                    key = f"flt_{label}_{col}"
                    current = st.session_state.get(key, "")
                    index = choices.index(current) if current in choices else 0

                    filters[col] = st.selectbox(
                        label=col,
                        options=choices,
                        index=index,
                        key=key
                    )

            # 4) Apply all selected filters to df
            df_filtered = df.copy()
            for col, val in filters.items():
                if val:
                    df_filtered = df_filtered[df_filtered[col].astype(str) == val]

            if df_filtered.empty:
                st.warning("No rows match your filters.")
                continue

            # 5) Display filtered table with original indices
            st.dataframe(df_filtered)

            # 6) Let user pick an actual row index to inspect
            idx = st.selectbox(
                "Select the original row index to inspect:",
                options=list(df_filtered.index),
                key=f"idx_{label}"
            )
            row = df_filtered.loc[idx]
            row_info = "; ".join(f"{col}: {row[col]}" for col in df_filtered.columns)
            st.markdown(f"**Selected Row {idx}:** {row_info}")
            st.markdown("---")

            # 7) Inject Generate-mode UI for this tab
            base      = label.replace(" ", "_").lower()
            hist_key  = f"filter_gen_history_{base}"
            inp_key   = f"filter_gen_input_{base}"
            btn_key   = f"filter_gen_send_{base}"
            clr_key   = f"filter_gen_clear_{base}"

            # Initialize session state
            if hist_key not in st.session_state:
                st.session_state[hist_key] = []
            if clr_key not in st.session_state:
                st.session_state[clr_key] = False

            # Handle Send button
            if st.button("Send", key=btn_key):
                msg = st.session_state.get(inp_key, "").strip()
                if msg:
                    st.session_state[hist_key].append(msg)
                    st.session_state[clr_key] = True
                else:
                    st.warning("Please enter a message to send.")

            # Clear the input if flagged
            if st.session_state[clr_key]:
                st.session_state[inp_key] = ""
                st.session_state[clr_key] = False

            # 7a) Default promo copy
            if label == "Upcoming Match":
                st.markdown(DEFAULT_MATCH_TEXT)
            elif label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)
            elif label == "Course":
                st.markdown(DEFAULT_COURSE_TEXT)
            elif label == "Article":
                st.markdown(DEFAULT_ARTICLE_TEXT)

            # 7b) Show any previous user inputs
            history = st.session_state[hist_key]
            if history:
                st.markdown("**Your Inputs So Far:**")
                for entry in history:
                    st.write(f"- {entry}")
                st.markdown("---")

            # 7c) Finally, the text_input widget
            st.text_input(f"Type your message for “{label}”…", key=inp_key)
