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

def embed_text(text: str, model: str = "text-embedding-ada-002") -> list[float]:
    """
    Embed an arbitrary piece of text via OpenAI.
    """
    resp = _client.embeddings.create(
        model=model,
        input=[text]
    )
    return resp.data[0].embedding

def get_best_matching_row(category: str, prompt: str, top_k: int = 1) -> pd.DataFrame:
    """
    Embed the prompt, query the Qdrant collection for `category`,
    and return the top-k payloads as a DataFrame.
    """
    collection = category.lower().replace(" ", "_")
    # 1) embed the prompt
    vector = embed_text(prompt)

    # 2) search Qdrant (only with_payload)
    hits = _qdrant.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
        with_payload=True,    # <-- keep this
        # remove with_vector argument entirely
    )

    # 3) extract payloads
    rows = [hit.payload for hit in hits]

    # 4) build DataFrame
    if rows:
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame()

# ─── Generate “fake row text” in the exact embedding format ─────────────────
def generate_fake_row_text(
    prompt: str,
    example_row: dict,
    chat_model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Given a user prompt and one example row (as a dict of col→value),
    ask the LLM to output a *single string* ready for embedding, in the
    exact format you used when you indexed:
        "ColA: valA  ColB: valB  ...  ColZ: valZ"
    """
    # 1) Build an actual example text from the row
    columns      = list(example_row.keys())
    example_text = "  ".join(f"{col}: {example_row[col]}" for col in columns)

    system = (
        "You are a data synthesizer.  A dataset was indexed by concatenating each "
        "column name with its cell value, separated by ': ' and two spaces.  "
        "Here is one real example of how a row was formatted:\n\n"
        f"{example_text}\n\n"
        "Given the user's description, produce exactly one line in that same format."
    )
    user = (
        f"Description: {prompt}\n\n"
        "Return *only* the single-line text, following exactly the pattern shown above."
    )

    resp = _client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def search_with_fake_row_ai(
    category: str,
    prompt: str,
    example_row: dict,
    top_k: int = 1,
    embed_model: str = "text-embedding-ada-002",
    chat_model: str = "gpt-4o"
) -> pd.DataFrame:
    """
    1) Generate a fake-row text using an *actual* example row for format
    2) Embed it exactly as you did for the real rows
    3) Query Qdrant for the nearest neighbors
    4) Return their payloads as a DataFrame
    """
    # 1) Synthesize the text to embed
    fake_text = generate_fake_row_text(prompt, example_row, chat_model=chat_model)

    # 2) Embed
    vec = embed_text(fake_text, model=embed_model)

    # 3) Search Qdrant
    collection = category.lower().replace(" ", "_")
    hits = _qdrant.search(
        collection_name=collection,
        query_vector=vec,
        limit=top_k,
        with_payload=True
    )

    # 4) Build DataFrame from payloads
    rows = [hit.payload for hit in hits]
    return pd.DataFrame(rows) if rows else pd.DataFrame()