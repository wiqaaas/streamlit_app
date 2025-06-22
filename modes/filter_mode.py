# modes/filter_mode.py

import os
import streamlit as st
import pandas as pd

from config import TAB_LABELS
from ai_client import generate_ad_copy, chat_conversation, PROMPT_TEMPLATES
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

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

@st.cache_data(show_spinner=False)
def load_all_dataframes():
    """Cache the four Excel reads once per session."""
    dfs = {}
    for label, fname in FILENAME_MAP.items():
        path = os.path.join(DATA_DIR, fname)
        dfs[label] = pd.read_excel(path)
    return dfs

def run_filter_mode():
    st.header("🔍 Dynamic Filter & Chat Mode")

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

            # 2) Clear All Filters
            if st.button("Clear All Filters", key=f"clear_filters_{label}"):
                for col in df.columns:
                    st.session_state[f"flt_{label}_{col}"] = ""

            # 3) Build interdependent exact-match filters
            st.markdown("**Filter by exact column values (select to narrow):**")
            filters = {}
            with st.expander("Show filters", expanded=False):
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

            # 4) Apply selected filters
            df_filtered = df.copy()
            for col, val in filters.items():
                if val:
                    df_filtered = df_filtered[df_filtered[col].astype(str) == val]

            if df_filtered.empty:
                st.warning("No rows match your filters.")
                continue

            # 5) Display filtered table (original indices)
            st.dataframe(df_filtered)

            # 6) Select an original row index
            idx = st.selectbox(
                "Select original row index to inspect:",
                options=list(df_filtered.index),
                key=f"idx_{label}"
            )
            selected_df = df_filtered.loc[[idx]]
            st.markdown(f"**Selected Row {idx}:**")
            st.dataframe(selected_df)
            st.markdown("---")

            # 7) Generate the initial Ad Copy
            if st.button("Generate Ad Copy", key=f"gen_ad_{label}"):
                info = selected_df.iloc[0].to_dict()
                with st.spinner("Generating ad copy…"):
                    ad_copy = generate_ad_copy(info, category=label)

                # Seed the chat history for this tab
                base     = label.replace(" ", "_").lower()
                chat_key = f"chat_history_{base}"

                # Build the seed messages exactly as sent
                tpl       = PROMPT_TEMPLATES[label]
                system_m  = tpl["system"]
                user_m    = tpl["user"].format(info=info)

                st.session_state[chat_key] = [
                    {"role": "system",    "content": system_m},
                    {"role": "user",      "content": user_m},
                    {"role": "assistant", "content": ad_copy},
                ]

                st.subheader("📣 Generated Ad Copy")
                st.write(ad_copy)
                st.markdown("---")

            # 8) Show default promo copy (optional)
            if label == "Upcoming Match":
                st.markdown(DEFAULT_MATCH_TEXT)
            elif label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)
            elif label == "Course":
                st.markdown(DEFAULT_COURSE_TEXT)
            elif label == "Article":
                st.markdown(DEFAULT_ARTICLE_TEXT)

            # 9) Chat interface (history + input)
            base      = label.replace(" ", "_").lower()
            chat_key  = f"chat_history_{base}"
            input_key = f"chat_input_{base}"

            if chat_key not in st.session_state:
                st.session_state[chat_key] = []

            # Render full chat history
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # Chat input box
            if prompt := st.chat_input("Type a follow-up prompt…", key=input_key):
                # append user turn
                st.session_state[chat_key].append({"role": "user", "content": prompt})
                # call OpenAI with full history
                with st.spinner("Thinking…"):
                    reply = chat_conversation(st.session_state[chat_key])
                # append & display assistant turn
                st.session_state[chat_key].append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"):
                    st.write(reply)
