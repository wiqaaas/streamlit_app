# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st

from config import TAB_LABELS, FILENAME_MAP
import ai_client
from ai_client import (
    generate_ad_copy,
    chat_conversation,
    PROMPT_TEMPLATES,
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

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # 1) Load DataFrame
            if label not in FILENAME_MAP:
                st.error(f"No filename mapped for tab “{label}”.")
                continue
            fname = FILENAME_MAP[label]
            try:
                df = pd.read_excel(os.path.join(DATA_DIR, fname))
            except Exception as e:
                st.error(f"Failed to load `{fname}`: {e}")
                continue

            # 2) Show full DataFrame
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Prepare session-state keys
            hist_key = f"history_{label.replace(' ', '_')}"
            info_key = f"best_info_{label.replace(' ', '_')}"
            init_history(hist_key)
            if info_key not in st.session_state:
                st.session_state[info_key] = None

            # 4) Semantic-search input (only runs when user types)
            prompt_key = f"input_{label.replace(' ', '_')}"
            prompt = st.chat_input("Type a message about this data…", key=prompt_key)
            if prompt:
                # record user message
                st.session_state[hist_key].append({"role": "user", "content": prompt})

                # run search with AI client
                best_df = ai_client.get_best_matching_row(
                    category=label,
                    prompt=prompt,
                    top_k=1
                )

                if not best_df.empty:
                    info = best_df.iloc[0].to_dict()
                    st.session_state[info_key] = info
                    st.session_state[hist_key].append({
                        "role": "assistant",
                        "content": f"Displayed best match for “{prompt}”"
                    })
                else:
                    st.session_state[info_key] = None
                    st.session_state[hist_key].append({
                        "role": "assistant",
                        "content": "No match found."
                    })

            # 5) Retrieve stored best-match for display & downstream actions
            info = st.session_state[info_key]
            if info:
                best_df = pd.DataFrame([info])
                st.markdown("### 🔍 Best Match")
                st.dataframe(best_df, use_container_width=True)

                st.markdown("---")
                st.subheader("⚙️ Generate & Chat Options")

                # a) Generate initial ad copy (does NOT re-run search)
                if st.button("Generate Ad Copy", key=f"gen_ad_{label}"):
                    with st.spinner("Generating ad copy…"):
                        ad_copy = generate_ad_copy(info, category=label)
                    st.subheader("📣 Generated Ad Copy")
                    st.write(ad_copy)
                    st.markdown("---")

                # b) Follow-up prompt input (also does NOT re-run search)
                follow_key = f"followup_{label.replace(' ', '_')}"
                followup = st.text_input("Type a follow-up prompt…", key=follow_key)
                if followup:
                    tpl = PROMPT_TEMPLATES[label]
                    system_msg = {"role": "system",  "content": tpl["system"]}
                    user_seed  = {"role": "user",    "content": tpl["user"].format(info=info)}
                    user_fu    = {"role": "user",    "content": followup}
                    messages   = [system_msg, user_seed, user_fu]
                    with st.spinner("Generating assistant response…"):
                        reply = chat_conversation(messages)
                    st.subheader("🤖 Assistant Response")
                    st.write(reply)
                    st.markdown("---")


                # default promo copy
                # if label == "Upcoming Match":
                #     st.markdown(DEFAULT_MATCH_TEXT)
                # elif label == "Lesson":
                #     st.markdown(DEFAULT_LESSON_TEXT)
                # elif label == "Course":
                #     st.markdown(DEFAULT_COURSE_TEXT)
                # elif label == "Article":
                #     st.markdown(DEFAULT_ARTICLE_TEXT)
