# ai_client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env (project root)
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment")

_client = OpenAI(api_key=API_KEY)

def generate_ad_copy(
    info: dict,
    system_prompt: str = (
        "You are best marketing manager who can create engaging ads "
        "for social media about polo games."
    ),
    model: str = "gpt-4o",
    temperature: float = 0.7
) -> str:
    """
    Given a dict of row data, call OpenAI to produce an Instagram ad copy.
    """
    user_prompt = (
        "Provide the best-performing Instagram ad copy for an upcoming match "
        "using the following details:\n"
        f"{info}\n"
        "Make it engaging, audience-focused, and tailored for social media impact."
    )
    resp = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content
