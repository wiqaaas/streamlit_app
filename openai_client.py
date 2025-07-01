import os
from dotenv import load_dotenv
from openai import OpenAI

# Load your .env (for OPENAI_API_KEY)
BASE = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(BASE, ".env"))

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

_client = OpenAI(api_key=_api_key)

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

def chat_conversation(
    messages: list[dict],
    model: str = "gpt-4.1-mini",
    temperature: float = 0.3
) -> str:
    """
    Continue a chat given a list of {'role':..., 'content':...} messages.
    Returns the assistant’s reply.
    """
    return get_completion(messages, model=model, temperature=temperature)
