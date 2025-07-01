import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_API_KEY = os.getenv("OPENAI_API_KEY")
_client = OpenAI(api_key=_API_KEY)

def get_completion(messages: list, model: str = "gpt-4o-mini", temperature: float = 0.3) -> str:
    resp = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content
