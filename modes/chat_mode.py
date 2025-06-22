import streamlit as st
import pandas as pd
from utils import init_history, generate_dummy_response
from config import TAB_LABELS, DATAFRAME_SOURCES

# DATAFRAME_SOURCES should be a dict mapping each tab label to a path or dataframe object.
# e.g. in config.py:
# DATAFRAME_SOURCES = {
#     "Upcoming Match": "data/upcoming_match.csv",
#     "Lesson": "data/lesson.csv",
#     "Course": "data/course.csv",
#     "Article": "data/article.csv",
# }

@st.cache_data
def load_dataframe(source):
    # Load dataframe from CSV or return if already a DataFrame
    if isinstance(source, pd.DataFrame):
        return source
    return pd.read_csv(source)


def run_chat_mode():
    st.header("💬 Chat Mode with Dataframes")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            key = f"history_{label.replace(' ', '_').lower()}"
            init_history(key)
            history = st.session_state[key]

            # 1) capture new message first
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{key}")
            if prompt:
                history.append({"role": "user", "content": prompt})
                reply = generate_dummy_response(prompt)
                history.append({"role": "assistant", "content": reply})

            # 2) show previous messages in an expander
            older = history[:-2]
            with st.expander("📜 Previous Messages", expanded=False):
                if not older:
                    st.info("No previous messages.")
                else:
                    for msg in older:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

            # 3) show the latest exchange
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # 4) Load and display the relevant dataframe
            source = DATAFRAME_SOURCES.get(label)
            if source is not None:
                df = load_dataframe(source)
                st.subheader(f"📊 Data for {label}")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(f"No dataframe configured for '{label}'")
