# modes/filter_mode.py

import os
import streamlit as st
import pandas as pd

from config import TAB_LABELS
from ai_client import generate_ad_copy, chat_conversation, PROMPT_TEMPLATES
from config import (
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

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

@st.cache_data(show_spinner=False)
def load_all_dataframes():
    dfs = {}
    for label, fname in FILENAME_MAP.items():
        path = os.path.join(DATA_DIR, fname)
        dfs[label] = pd.read_excel(path)
    return dfs

def run_filter_mode():
    st.header("🔍 Filter & Generate Mode")

    dfs = load_all_dataframes()
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            df = dfs.get(label)
            if df is None:
                st.error(f"No data for **{label}**.")
                continue

            st.subheader(f"📊 {label}")

            # Clear filters
            if st.button("Clear All Filters", key=f"clear_filters_{label}"):
                for col in df.columns:
                    st.session_state[f"flt_{label}_{col}"] = ""

            # Interdependent exact-match filters
            filters = {}
            with st.expander("Show filters", expanded=False):
                st.markdown("**Filter by exact column values:**")
                for col in df.columns:
                    temp = df.copy()
                    for other in df.columns:
                        if other == col: 
                            continue
                        val_other = st.session_state.get(f"flt_{label}_{other}", "")
                        if val_other:
                            temp = temp[temp[other].astype(str) == val_other]

                    opts = [""] + sorted(temp[col].dropna().astype(str).unique())
                    key = f"flt_{label}_{col}"
                    curr = st.session_state.get(key, "")
                    idx  = opts.index(curr) if curr in opts else 0
                    filters[col] = st.selectbox(col, opts, index=idx, key=key)

            # Apply filters
            df_filtered = df.copy()
            for col, val in filters.items():
                if val:
                    df_filtered = df_filtered[df_filtered[col].astype(str) == val]

            if df_filtered.empty:
                st.warning("No rows match your filters.")
                continue

            st.dataframe(df_filtered)

            # Select and show one row as DataFrame
            idx = st.selectbox(
                "Select row index to inspect:",
                options=list(df_filtered.index),
                key=f"idx_{label}"
            )
            selected_df = df_filtered.loc[[idx]]
            st.markdown(f"**Selected Row {idx}:**")
            st.dataframe(selected_df)
            st.markdown("---")

            # Generate initial ad copy
            if st.button("Generate Ad Copy", key=f"gen_ad_{label}"):
                info = selected_df.iloc[0].to_dict()
                with st.spinner("Generating ad copy…"):
                    ad_copy = generate_ad_copy(info, category=label)
                st.subheader("📣 Generated Ad Copy")
                st.write(ad_copy)
                st.markdown("---")

            # Text input for follow-up prompts
            input_key = f"chat_input_{label}"
            if prompt := st.text_input("Type follow-up prompt…", key=input_key):
                # Build message history internally
                base = label
                tpl  = PROMPT_TEMPLATES[base]
                system_msg = tpl["system"]
                user_msg   = tpl["user"].format(info=selected_df.iloc[0].to_dict())

                # Send system + user seed + new user prompt
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": user_msg},
                    {"role": "user",   "content": prompt},
                ]
                with st.spinner("Generating response…"):
                    reply = chat_conversation(messages)

                # Only show the fresh assistant reply
                st.subheader("Assistant Response")
                st.write(reply)
                st.markdown("---")

            # Optional default promo copy below
            # if label == "Upcoming Match":
            #     st.markdown(DEFAULT_MATCH_TEXT)
            # elif label == "Lesson":
            #     st.markdown(DEFAULT_LESSON_TEXT)
            # elif label == "Course":
            #     st.markdown(DEFAULT_COURSE_TEXT)
            # elif label == "Article":
            #     st.markdown(DEFAULT_ARTICLE_TEXT)
