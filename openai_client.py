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

# ─── Core Helpers ─────────────────────────────────────────────────
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
    # Only user and assistant turns go into the summary prompt
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
    If total tokens ≤ threshold: return messages as-is.
    Otherwise:
      1) keep ONLY the system messages
      2) summarize all user+assistant turns into one system message
      3) return [<all_system_msgs>, <HISTORY_SUMMARY>]
    """
    if _count_tokens(messages, model) <= threshold:
        return messages

    # 1) Pull out all system messages
    system_messages = [m for m in messages if m["role"] == "system"]

    # 2) Summarize the chat turns
    summary = _summarize_history(messages, model, temperature)
    summary_msg = {"role": "system", "content": f"<HISTORY_SUMMARY>\n{summary}"}

    # 3) Return system context + summary
    return system_messages + [summary_msg]

# ─── Public API ──────────────────────────────────────────────────
def chat_conversation(
    messages: list[dict],
    model: str = "gpt-4.1-mini",
    temperature: float = 0.3,
    token_threshold: int = 1000
) -> str:
    """
    Continue a chat given a list of messages.
    Automatically summarizes if over `token_threshold`, 
    **while preserving ALL system messages**.
    Returns the assistant’s reply.
    """
    to_send = _prepare_messages(messages, token_threshold, model, temperature)
    return get_completion(to_send, model=model, temperature=temperature)
