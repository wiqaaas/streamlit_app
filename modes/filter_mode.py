# modes/filter_mode.py

import os
import streamlit as st
import pandas as pd

from config import TAB_LABELS
from ai_client import generate_ad_copy
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

            # 2) “Clear All Filters” button
            if st.button("Clear All Filters", key=f"clear_filters_{label}"):
                for col in df.columns:
                    st.session_state[f"flt_{label}_{col}"] = ""

            # 3) Build interdependent exact‐match filters
            st.markdown("**Filter by exact column values (select to narrow):**")
            filters = {}
            with st.expander("Show filters", expanded=False):
                for col in df.columns:
                    # Apply other filters first
                    temp = df.copy()
                    for other in df.columns:
                        if other == col:
                            continue
                        val_other = st.session_state.get(f"flt_{label}_{other}", "")
                        if val_other:
                            temp = temp[temp[other].astype(str) == val_other]

                    # Gather valid choices for this column
                    opts = [""] + sorted(temp[col].dropna().astype(str).unique())
                    key = f"flt_{label}_{col}"
                    current = st.session_state.get(key, "")
                    idx = opts.index(current) if current in opts else 0

                    filters[col] = st.selectbox(
                        label=col,
                        options=opts,
                        index=idx,
                        key=key
                    )

            # 4) Apply all selected filters
            df_filtered = df.copy()
            for col, val in filters.items():
                if val:
                    df_filtered = df_filtered[df_filtered[col].astype(str) == val]

            if df_filtered.empty:
                st.warning("No rows match your filters.")
                continue

            # 5) Display filtered DataFrame (original indices)
            st.dataframe(df_filtered)

            # 6) Pick an original row index to inspect
            idx = st.selectbox(
                "Select original row index to inspect:",
                options=list(df_filtered.index),
                key=f"idx_{label}"
            )

            # 7) Show that single row as a DataFrame
            selected_row_df = df_filtered.loc[[idx]]
            st.markdown(f"**Selected Row {idx}:**")
            st.dataframe(selected_row_df)
            st.markdown("---")

            # 8) “Generate Ad Copy” button
            if st.button("Generate Ad Copy", key=f"gen_ad_{label}"):
                # Extract row data as dict
                row_info = selected_row_df.iloc[0].to_dict()
                with st.spinner("Generating ad copy…"):
                    ad_copy = generate_ad_copy(row_info)

                st.subheader("📣 Generated Ad Copy")
                st.write(ad_copy)
                st.markdown("---")

            # 9) Default promo copy (optional)
            if label == "Upcoming Match":
                st.markdown(DEFAULT_MATCH_TEXT)
            elif label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)
            elif label == "Course":
                st.markdown(DEFAULT_COURSE_TEXT)
            elif label == "Article":
                st.markdown(DEFAULT_ARTICLE_TEXT)
