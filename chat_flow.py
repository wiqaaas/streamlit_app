# chat_flow.py
from openai_client import chat_conversation

def ask_model(history, user_message, model="gpt-4.1-mini", token_threshold=None):
    # append the new user message
    convo = history + [{"role":"user","content":user_message}]
    # get reply
    reply = chat_conversation(
        convo,
        model=model,
        token_threshold=token_threshold
    )
    # record both turns
    history.append({"role":"user","content":user_message})
    history.append({"role":"assistant","content":reply})
    return reply
