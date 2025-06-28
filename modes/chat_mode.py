# modes/chat_mode.py

import os
import pandas as pd
import streamlit as st
import numpy as np
from openai import OpenAI

from config import TAB_LABELS, FILENAME_MAP
from utils import init_history

# ——— Project & data paths ———
BASE_DIR     = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

# ——— OpenAI client instantiation ———
# Make sure OPENAI_API_KEY is set in your environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# ——— Caching data + embeddings ———
@st.cache_data(show_spinner=False)
def load_data_and_embeddings(fname: str) -> tuple[pd.DataFrame, dict[int, list[float]]]:
    """Load Excel into a DataFrame and compute an embedding for each row."""
    path = os.path.join(DATA_DIR, fname)
    df = pd.read_excel(path)
    row_embeds: dict[int, list[float]] = {}
    for idx, row in df.iterrows():
        # concatenate all columns for a holistic row representation
        text = "  ".join(f"{col}: {row[col]}" for col in df.columns)
        resp = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]
        )
        row_embeds[idx] = resp.data[0].embedding
    return df, row_embeds

@st.cache_data(show_spinner=False)
def embed_prompt(prompt: str) -> list[float]:
    """Embed the user’s prompt text."""
    resp = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[prompt]
    )
    return resp.data[0].embedding

# ——— Similarity & lookup ———
def find_best_row_index(
    row_embeds: dict[int, list[float]],
    prompt_embed: list[float]
) -> int | None:
    """Return index of the row whose embedding is most similar to the prompt."""
    best_idx, best_score = None, -1.0
    p_vec = np.array(prompt_embed)
    p_norm = np.linalg.norm(p_vec)
    for idx, emb in row_embeds.items():
        r_vec = np.array(emb)
        score = float(np.dot(p_vec, r_vec) / (p_norm * np.linalg.norm(r_vec)))
        if score > best_score:
            best_score, best_idx = score, idx
    return best_idx

# ——— Main chat mode ———
def run_chat_mode():
    st.header("💬 Chat Mode")
    tabs = st.tabs(TAB_LABELS)

    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            history_key = f"history_{label.replace(' ', '_').lower()}"
            init_history(history_key)
            history = st.session_state[history_key]

            # 1) Load DataFrame + embeddings once (cached)
            fname = FILENAME_MAP.get(label)
            if not fname:
                st.warning(f"No filename mapped for tab “{label}”.")
                continue
            df, row_embeds = load_data_and_embeddings(fname)

            # 2) Display full DataFrame at the top
            st.markdown("### 📊 Data Preview")
            st.dataframe(df, use_container_width=True)

            # 3) Chat input box
            prompt = st.chat_input(f"Type a message in “{label}”…", key=f"input_{history_key}")
            if prompt:
                # record user message
                history.append({"role": "user", "content": prompt})

                # embed & find best row
                p_emb = embed_prompt(prompt)
                best_idx = find_best_row_index(row_embeds, p_emb)

                # display matched row
                if best_idx is not None:
                    best_row = df.loc[[best_idx]]
                    st.markdown("### 🔍 Best Match")
                    st.dataframe(best_row, use_container_width=True)
                else:
                    st.info("No matching row found.")

                # record assistant action in history (optional)
                history.append({
                    "role": "assistant",
                    "content": f"Displayed row {best_idx}" if best_idx is not None else "No match"
                })

            # 4) Show previous messages
            older = history[:-2]
            with st.expander("📜 Previous Messages", expanded=False):
                if not older:
                    st.info("No previous messages.")
                else:
                    for msg in older:
                        with st.chat_message(msg["role"]):
                            st.write(msg["content"])

            # 5) Show the latest exchange inline
            current = history[-2:] if len(history) >= 2 else history
            for msg in current:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
