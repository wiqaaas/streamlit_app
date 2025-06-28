# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st
import openai
import numpy as np

from utils import init_history, generate_dummy_response
from config import TAB_LABELS, FILENAME_MAP

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

# Make sure your OpenAI key is set in the environment
openai.api_key = os.getenv("OPENAI_API_KEY", "")

@st.cache_data(show_spinner=False)
def load_dataframe(fname: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, fname)
    return pd.read_excel(path)

@st.cache_data(show_spinner=False)
def compute_row_embeddings(df: pd.DataFrame) -> dict[int, list[float]]:
    """
    Compute an embedding for each row by concatenating all columns (as strings).
    Returns a dict mapping row index -> embedding vector.
    """
    embeddings: dict[int, list[float]] = {}
    for idx, row in df.iterrows():
        # Turn every column (name + value) into one long string
        text = "  ".join(f"{col}: {row[col]}" for col in df.columns)
        resp = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings[idx] = resp["data"][0]["embedding"]
    return embeddings

def embed_prompt(prompt: str) -> list[float]:
    """Get an embedding for the user prompt."""
    resp = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=prompt
    )
    return resp["data"][0]["embedding"]

def find_best_row(df: pd.DataFrame,
                  row_embeds: dict[int, list[float]],
                  prompt_embed: list[float]
                 ) -> int | None:
    """Compute cosine similarity and return the index of the best‐matching row."""
    best_idx, best_score = None, -1.0
    p_vec = np.array(prompt_embed)
    p_norm = np.linalg.norm(p_vec)
    for idx, emb in row_embeds.items():
        r_vec = np.array(emb)
        score = float(np.dot(p_vec, r_vec) / (p_norm * np.linalg.norm(r_vec)))
        if score > best_score:
            best_score, best_idx = score, idx
    return best_idx

def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            history_key = f"history_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            history = st.session_state[history_key]

            # 1) Chat input first so it updates immediately
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{history_key}")
            if prompt:
                # append user message
                history.append({"role": "user", "content": prompt})
                # dummy reply
                reply = generate_dummy_response(prompt)
                history.append({"role": "assistant", "content": reply})

                # now do filtering via OpenAI embeddings
                fname = FILENAME_MAP.get(label)
                if fname:
                    df = load_dataframe(fname)
                    row_embeds = compute_row_embeddings(df)
                    p_embed = embed_prompt(prompt)
                    best_idx = find_best_row(df, row_embeds, p_embed)

                    if best_idx is not None:
                        best_row = df.loc[[best_idx]]
                        st.markdown(f"### 📊 Best match from `{fname}` (row {best_idx})")
                        st.dataframe(best_row, use_container_width=True)
                    else:
                        st.info("No matching row found.")
                else:
                    st.warning(f"No filename mapped for tab `{label}`.")

            # 2) Show older messages in an expander
            older = history[:-2]
            with st.expander("📜 Previous Messages", expanded=False):
                if not older:
                    st.info("No previous messages.")
                else:
                    for msg in older:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

            # 3) Show the latest exchange inline
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
