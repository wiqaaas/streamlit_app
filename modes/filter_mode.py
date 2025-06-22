# modes/filter_mode.py
import os
import streamlit as st
import pandas as pd
from config import TAB_LABELS

# Map each tab to its Excel filename
FILENAME_MAP = {
    "Upcoming Match": "df_schedule.xlsx",
    "Lesson":         "df_lessons.xlsx",
    "Course":         "df_courses.xlsx",
    "Article":        "df_article_schedule.xlsx",
}

# Compute paths
BASE_DIR     = os.path.dirname(__file__)                     # your_project/modes
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")            # your_project/data

def run_filter_mode():
    st.header("🔍 Column-Filter & Inspect Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            st.subheader(f"📊 {label} Data")

            # 1) Load the Excel for this tab
            filename = FILENAME_MAP.get(label)
            path = os.path.join(DATA_DIR, filename)
            try:
                df = pd.read_excel(path)
            except Exception as e:
                st.error(f"Failed to load `{filename}`: {e}")
                continue

            # 2) Build exact-match filters for each column
            st.markdown("**Filter by exact column values (leave blank to skip):**")
            filters = {}
            with st.expander("Show filters", expanded=False):
                for col in df.columns:
                    filters[col] = st.text_input(
                        f"{col}",
                        key=f"filter_{label.replace(' ', '_')}_{col}"
                    )

            # 3) Apply filters
            df_filtered = df.copy()
            for col, val in filters.items():
                if val != "":
                    # compare as strings to allow mixed dtypes
                    df_filtered = df_filtered[df_filtered[col].astype(str) == val]

            if df_filtered.empty:
                st.warning("No rows match your filters.")
            else:
                st.dataframe(df_filtered)

            # 4) Let user pick a row from the *filtered* view
            max_idx = len(df_filtered) - 1
            if max_idx >= 0:
                idx = st.number_input(
                    f"Enter row index to inspect (0 to {max_idx}):",
                    min_value=0,
                    max_value=max_idx,
                    step=1,
                    key=f"row_idx_{label.replace(' ', '_')}"
                )
                if st.button(
                    f"Show row {idx} info",
                    key=f"show_row_{label.replace(' ', '_')}"
                ):
                    row = df_filtered.iloc[idx]
                    info = "; ".join(f"{col}: {row[col]}" for col in df_filtered.columns)
                    st.markdown(f"**Row {idx} data:** {info}")
            else:
                st.info("No data left after filtering.")
