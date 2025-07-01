import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# ─── Setup ────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(BASE, ".env"))

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

_client = OpenAI(api_key=_api_key)

# ─── Helpers ──────────────────────────────────────────────────────
def get_completion(
    messages: list[dict],
    model: str = "gpt-4.1-mini",
    temperature: float = 0.3
) -> str:
    resp = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

def _count_tokens(messages: list[dict], model: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return sum(len(enc.encode(m["content"])) for m in messages)

def _summarize_history(
    messages: list[dict],
    model: str,
    temperature: float
) -> str:
    convo = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in messages
        if m["role"] in ("user", "assistant")
    )
    summary_prompt = [
        {"role": "system", "content": "You are a concise summarizer."},
        {"role": "user",   "content": convo}
    ]
    return get_completion(summary_prompt, model=model, temperature=temperature)

def _prepare_messages(
    messages: list[dict],
    threshold: int,
    model: str,
    temperature: float
) -> list[dict]:
    """
    If token count ≤ threshold: return messages as-is.
    Otherwise: summarize user+assistant turns into one SYSTEM message.
    """
    if _count_tokens(messages, model) <= threshold:
        return messages

    # summarize and reset history
    summary = _summarize_history(messages, model, temperature)
    base = messages[0]   # your initial SYSTEM
    date = messages[1]   # your "Today is ..." SYSTEM
    return [
        base,
        date,
        {"role": "system", "content": f"<HISTORY_SUMMARY>\n{summary}"}
    ]

# ─── Public API ──────────────────────────────────────────────────
def chat_conversation(
    messages: list[dict],
    model: str = "gpt-4.1-mini",
    temperature: float = 0.3,
    token_threshold: int = 1000
) -> str:
    """
    Continue a chat given a list of messages.
    Automatically summarizes if over `token_threshold`.
    Returns the assistant’s reply.
    """
    to_send = _prepare_messages(messages, token_threshold, model, temperature)
    return get_completion(to_send, model=model, temperature=temperature)
