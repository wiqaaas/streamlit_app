# ai_client.py

import os
import pandas as pd
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from config import FILENAME_MAP, DATA_DIR, TAB_LABELS

# 1) Load .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment")

# 2) Instantiate client
_client = OpenAI(api_key=API_KEY)

PROMPT_TEMPLATES = {
    "Upcoming Match": {
        "system": (
            "You are the world’s top-tier social media strategist for polo events. "
            "Your job is to craft high-converting Instagram ads that build excitement and drive viewer engagement."
        ),
        "user": (
            "Using the following match details:\n{info}\n"
            "Create a compelling Instagram ad caption that captures the energy of the upcoming game. "
            "Make it visually engaging, emotionally resonant, and optimized to stop the scroll. "
            "Include a sense of urgency, key match details, and a call to watch or follow."
        ),
    },
    "Lesson": {
        "system": (
            "You are a high-converting Instagram ad copywriter specializing in sports education. "
            "Your goal is to drive sign-ups and spark interest in polo training content."
        ),
        "user": (
            "Given the following lesson details:\n{info}\n"
            "Write an Instagram ad caption that highlights what the lesson teaches, why it matters, and who it's for. "
            "Use a confident tone, include benefits, and end with a clear call to action (e.g., 'Watch now', 'Master your next move')."
        ),
    },
    "Course": {
        "system": (
            "You are a results-driven digital marketer focused on promoting online sports courses. "
            "Your specialty is writing irresistible Instagram captions that boost enrollment."
        ),
        "user": (
            "Based on this course information:\n{info}\n"
            "Write an Instagram ad that makes the course feel essential for anyone looking to level up their polo skills. "
            "Highlight outcomes, target audience, and create FOMO with urgency cues (e.g., 'Limited spots', 'Enroll now')."
        ),
    },
    "Article": {
        "system": (
            "You are a social media content strategist for a leading polo media brand. "
            "You excel at turning long-form content into short, click-worthy Instagram captions."
        ),
        "user": (
            "Using the article info below:\n{info}\n"
            "Write a teaser Instagram caption that hooks attention, hints at the value of the article, and encourages followers to click the link or visit the site to read more. "
            "Use emotion, curiosity, or controversy if applicable."
        ),
    },
}

def generate_ad_copy(
    info: dict,
    category: str,
    model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Given a dict of row data and a category (one of TAB_LABELS),
    call OpenAI to produce tailored Instagram ad copy.
    """
    if category not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown category: {category}")

    tpl = PROMPT_TEMPLATES[category]
    system_prompt = tpl["system"]
    user_prompt   = tpl["user"].format(info=info)

    resp = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content

def chat_conversation(
    messages: list[dict],
    model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Continue a chat given a list of {'role':..., 'content':...} messages.
    Returns the assistant’s reply.
    """
    resp = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

# ——— Data + embedding logic ———

@st.cache_data(show_spinner=False)
def load_data_and_embeddings(category: str) -> tuple[pd.DataFrame, dict[int, list[float]]]:
    """
    Load the Excel file for this category and compute an embedding for each row (cached).
    Returns (df, {row_index: embedding}).
    """
    if category not in FILENAME_MAP:
        raise ValueError(f"No filename mapped for category “{category}”")
    fname = FILENAME_MAP[category]
    path = os.path.join(DATA_DIR, fname)
    df = pd.read_excel(path)

    row_embeds: dict[int, list[float]] = {}
    for idx, row in df.iterrows():
        # Build a single string containing all column names & values
        text = "  ".join(f"{col}: {row[col]}" for col in df.columns)
        resp = _client.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]
        )
        row_embeds[idx] = resp.data[0].embedding

    return df, row_embeds

@st.cache_data(show_spinner=False)
def embed_text(text: str) -> list[float]:
    """Embed an arbitrary piece of text (cached)."""
    resp = _client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return resp.data[0].embedding

def find_best_row_index(
    row_embeds: dict[int, list[float]],
    prompt_emb: list[float]
) -> int | None:
    """Return the row index whose embedding is most similar (cosine) to the prompt."""
    best_idx, best_score = None, -1.0
    p_vec = np.array(prompt_emb)
    p_norm = np.linalg.norm(p_vec)

    for idx, emb in row_embeds.items():
        r_vec = np.array(emb)
        score = float(np.dot(p_vec, r_vec) / (p_norm * np.linalg.norm(r_vec)))
        if score > best_score:
            best_score, best_idx = score, idx

    return best_idx

def get_best_matching_row(category: str, prompt: str) -> pd.DataFrame:
    """
    Convenience wrapper: load data+embeddings, embed prompt, find best row,
    and return it as a single-row DataFrame (or empty DF if no match).
    """
    df, row_embeds = load_data_and_embeddings(category)
    prompt_emb = embed_text(prompt)
    best_idx = find_best_row_index(row_embeds, prompt_emb)

    if best_idx is not None:
        return df.loc[[best_idx]]
    else:
        return pd.DataFrame(columns=df.columns)