# ai_client.py

import os
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse

# 1) Load environment
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

if not API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment")
if not QDRANT_URL:
    raise ValueError("Missing QDRANT_URL in environment")

# 2) Instantiate clients
_client = OpenAI(api_key=API_KEY)
_qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

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

# ——— Embedding utilities ———

def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    resp = _client.embeddings.create(model=model, input=[text])
    return resp.data[0].embedding

def get_best_matching_row(category: str, prompt: str, top_k: int = 1) -> pd.DataFrame:
    """
    Your existing Qdrant search—it returns a DataFrame of payload rows (or empty).
    """
    collection = category.lower().replace(" ", "_")
    vec        = embed_text(prompt)
    hits       = _qdrant.search(
        collection_name=collection,
        query_vector=vec,
        limit=top_k,
        with_payload=True
    )
    rows = [hit.payload for hit in hits]
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ─── New: row description helper ────────────────────────────────────────────
def describe_row(
    row: pd.Series,
    model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Given one DataFrame row (as a Series), prompt the LLM to write a concise
    one-paragraph description, mentioning only non-null fields.
    """
    row_lines = "\n".join(f"{col}: {row[col]}" for col in row.index if pd.notna(row[col]))
    prompt = (
        "You are a data summarizer.  I will give you a single record from a dataset "
        "as key/value pairs. Please write a one-paragraph description of this record "
        "in plain English, mentioning only the fields that have values.\n\n"
        f"{row_lines}\n\n"
        "Description:"
    )
    resp = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You summarize database rows."},
            {"role": "user",   "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

# ─── New: combine search + description ──────────────────────────────────────
def get_best_match_with_description(
    category: str,
    prompt: str,
    top_k: int = 1,
    desc_model: str = "gpt-4o",
    desc_temp: float = 0.7
) -> tuple[pd.DataFrame, str]:
    """
    1) Run the Qdrant search to get the top-k rows.
    2) If non-empty, take the first row and generate a human description.
    Returns (DataFrame, description_string).
    """
    df = get_best_matching_row(category, prompt, top_k)
    if df.empty:
        return df, ""
    # describe only the first match
    description = describe_row(df.iloc[0], model=desc_model, temperature=desc_temp)
    return df, description