# modes/centralized_mode.py

import os
import pandas as pd
import streamlit as st

from config import TAB_LABELS, FILENAME_MAP
import ai_client
from ai_client import (
    generate_ad_copy,
    chat_conversation,
    PROMPT_TEMPLATES,
    get_best_matching_row
)
from utils import init_history
from config import (
    DEFAULT_MATCH_TEXT,
    DEFAULT_LESSON_TEXT,
    DEFAULT_COURSE_TEXT,
    DEFAULT_ARTICLE_TEXT,
)

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")


def run_centralized_mode():
    st.header("💬 Centralized Chat & Ad Generator")

    # 1) Load all dataframes once
    dfs = {}
    for label, fname in FILENAME_MAP.items():
        path = os.path.join(DATA_DIR, fname)
        try:
            dfs[label] = pd.read_excel(path)
        except Exception as e:
            st.error(f"Failed to load `{fname}`: {e}")
            return

    # 2) Initialize a single chat history
    hist_key = "history_central"
    init_history(hist_key)

    # 3) Single chat input for semantic search across all categories
    prompt = st.chat_input("Type a query to find relevant rows across all categories…", key="central_input")
    if prompt:
        st.session_state[hist_key].append({"role": "user", "content": prompt})
        # 4) For each category, retrieve its best-matching row
        st.session_state["central_best_rows"] = {}
        for label, df in dfs.items():
            best_df = get_best_matching_row(label, prompt, top_k=1)
            if not best_df.empty:
                info = best_df.iloc[0].to_dict()
                st.session_state["central_best_rows"][label] = info
            else:
                st.session_state["central_best_rows"][label] = {}
        st.session_state[hist_key].append({
            "role": "assistant",
            "content": "Found relevant rows for each category."
        })

    # 5) Display the retrieved rows
    best_rows = st.session_state.get("central_best_rows", {})
    if best_rows:
        st.markdown("### 🔍 Best Matches")
        for label, info in best_rows.items():
            st.markdown(f"**{label}:**")
            if info:
                st.dataframe(pd.DataFrame([info]), use_container_width=True)
            else:
                st.write("_No match found_")
        st.markdown("---")

        # 6) Generate a single unified ad from the four rows
        if st.button("Generate Unified Ad"):
            details = "\n\n".join(
                f"{label} details: {info}"
                for label, info in best_rows.items() if info
            )
            system_msg = {
                "role": "system",
                "content": (
                    "You are a world-class social media strategist skilled at "
                    "combining multiple pieces of content into one cohesive Instagram ad caption."
                )
            }
            user_msg = {
                "role": "user",
                "content": (
                    f"Using the following details from each category:\n{details}\n\n"
                    "Create a single, compelling Instagram ad caption that weaves them together."
                )
            }
            st.session_state[hist_key].append(system_msg)
            st.session_state[hist_key].append(user_msg)

            with st.spinner("Generating unified ad…"):
                ad = chat_conversation([system_msg, user_msg])
            st.subheader("📣 Unified Ad")
            st.write(ad)
            st.markdown("---")

            st.session_state[hist_key].append({"role": "assistant", "content": ad})

        # 7) Follow-up chat to refine the ad
        followup = st.text_input("Type follow-up prompt to refine the ad…", key="central_followup")
        if followup:
            st.session_state[hist_key].append({"role": "user", "content": followup})
            with st.spinner("Generating assistant response…"):
                reply = chat_conversation(st.session_state[hist_key])
            st.subheader("🤖 Assistant Response")
            st.write(reply)
            st.markdown("---")
            st.session_state[hist_key].append({"role": "assistant", "content": reply})
