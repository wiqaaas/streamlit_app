# utils.py
import streamlit as st

def init_history(key: str):
    if key not in st.session_state:
        st.session_state[key] = []

def generate_dummy_response(user_input: str) -> str:
    # stub for your real API call
    return f"🤖 DummyBot: You said “{user_input}”"
