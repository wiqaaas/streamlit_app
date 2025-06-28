# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st

from config import TAB_LABELS, FILENAME_MAP
import ai_client
from ai_client import get_best_matching_row, generate_ad_copy, chat_conversation, PROMPT_TEMPLATES
from modes.generate_mode import (
    DEFAULT_MATCH_TEXT,
    DEFAULT_LESSON_TEXT,
    DEFAULT_COURSE_TEXT,
    DEFAULT_ARTICLE_TEXT,
)
from utils import init_history

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # 1) Load DataFrame from disk
            if label not in FILENAME_MAP:
                st.error(f"No filename mapped for tab “{label}”.")
                continue

            fname     = FILENAME_MAP[label]
            file_path = os.path.join(DATA_DIR, fname)
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                st.error(f"Failed to load `{fname}`: {e}")
                continue

            # 2) Show the full DataFrame
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Chat input for semantic search
            history_key = f"history_{label.replace(' ', '_').lower()}"
            input_key   = f"input_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            prompt = st.chat_input(f"Type a message about this data…", key=input_key)

            best_row = pd.DataFrame()
            if prompt:
                st.session_state[history_key].append({"role": "user", "content": prompt})

                best_row = get_best_matching_row(label, prompt)
                if not best_row.empty:
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                    st.session_state[history_key].append({
                        "role": "assistant",
                        "content": f"Displayed best match for “{prompt}”"
                    })
                else:
                    st.info("No matching row found.")
                    st.session_state[history_key].append({
                        "role": "assistant",
                        "content": "No match found."
                    })

            # 4) If a row was found, show filter-mode style interface
            if not best_row.empty:
                info = best_row.iloc[0].to_dict()

                st.markdown("---")
                st.subheader("⚙️ Generate & Chat Options")

                # Generate initial ad copy
                if st.button("Generate Ad Copy", key=f"gen_ad_{label}"):
                    with st.spinner("Generating ad copy…"):
                        ad_copy = generate_ad_copy(info, category=label)
                    st.subheader("📣 Generated Ad Copy")
                    st.write(ad_copy)
                    st.markdown("---")

                # Follow-up prompt
                followup_key = f"chat_input_{label}"
                if followup := st.text_input("Type follow-up prompt…", key=followup_key):
                    tpl = PROMPT_TEMPLATES[label]
                    system_msg = {"role": "system",  "content": tpl["system"]}
                    user_seed  = {"role": "user",    "content": tpl["user"].format(info=info)}
                    user_fu    = {"role": "user",    "content": followup}
                    messages   = [system_msg, user_seed, user_fu]

                    with st.spinner("Generating response…"):
                        reply = chat_conversation(messages)

                    st.subheader("Assistant Response")
                    st.write(reply)
                    st.markdown("---")

                # Optional default promo copy
                if label == "Upcoming Match":
                    st.markdown(DEFAULT_MATCH_TEXT)
                elif label == "Lesson":
                    st.markdown(DEFAULT_LESSON_TEXT)
                elif label == "Course":
                    st.markdown(DEFAULT_COURSE_TEXT)
                elif label == "Article":
                    st.markdown(DEFAULT_ARTICLE_TEXT)
