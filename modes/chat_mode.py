# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st
import openai
import numpy as np

from config import TAB_LABELS, FILENAME_MAP

# Compute project & data paths
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY", "")

@st.cache_data(show_spinner=False)
def load_data(fname: str) -> tuple[pd.DataFrame, dict[int, list[float]]]:
    """
    Load the Excel file once and pre-compute an embedding for each row.
    Returns (df, row_embeddings).
    """
    path = os.path.join(DATA_DIR, fname)
    df = pd.read_excel(path)
    row_embeds: dict[int, list[float]] = {}
    for idx, row in df.iterrows():
        # Concatenate all columns into one string
        text = "  ".join(f"{col}: {row[col]}" for col in df.columns)
        resp = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]
        )
        row_embeds[idx] = resp.data[0].embedding
    return df, row_embeds

@st.cache_data(show_spinner=False)
def embed_prompt(prompt: str) -> list[float]:
    """Embed the user’s prompt."""
    resp = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[prompt]
    )
    return resp.data[0].embedding

def find_best_row(
    df: pd.DataFrame,
    row_embeds: dict[int, list[float]],
    prompt_embed: list[float]
) -> int | None:
    """Find the row index whose embedding is most similar to the prompt."""
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
            # 1) Load (and cache) the DataFrame + row embeddings
            fname = FILENAME_MAP.get(label)
            if not fname:
                st.warning(f"No filename mapped for tab “{label}”.")
                continue
            df, row_embeds = load_data(fname)

            # 2) Show the full DataFrame at the top
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Chat input
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{label}")
            if prompt:
                # 4) Embed prompt and find best row
                p_embed = embed_prompt(prompt)
                best_idx = find_best_row(df, row_embeds, p_embed)

                # 5) Display the single best-matching row
                if best_idx is not None:
                    best_row = df.loc[[best_idx]]
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                else:
                    st.info("No matching row found.")
