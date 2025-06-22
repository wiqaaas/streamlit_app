# modes/filter_mode.py
import streamlit as st
import pandas as pd
from config import TAB_LABELS

# Map each tab to its Excel filename
FILENAME_MAP = {
    "Upcoming Match":     "df_schedule.xlsx",
    "Lesson":             "df_lessons.xlsx",
    "Course":             "df_courses.xlsx",
    "Article":            "df_article_schedule.xlsx",
}

def run_filter_mode():
    st.header("🔍 Filter Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            filename = FILENAME_MAP.get(label)
            if not filename:
                st.error(f"No filename configured for tab **{label}**.")
                continue

            # 1) Load the specific Excel file for this tab
            try:
                df = pd.read_excel(filename)
                st.subheader(f"📊 Data for {label} (from `{filename}`)")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Failed to load `{filename}`: {e}")
                continue

            # 2) Pick a row index
            idx = st.number_input(
                f"Enter row index for **{label}** (0 to {len(df)-1}):",
                min_value=0,
                max_value=max(0, len(df)-1),
                step=1,
                key=f"row_idx_{label.replace(' ', '_').lower()}"
            )

            # 3) On button click, display that row as a single-line string
            if st.button(f"Show row {idx} info", key=f"show_row_{label.replace(' ', '_').lower()}"):
                try:
                    row = df.iloc[idx]
                    info = "; ".join(f"{col}: {row[col]}" for col in df.columns)
                    st.markdown(f"**Row {idx} data:** {info}")
                except Exception as e:
                    st.error(f"Could not read row {idx}: {e}")
