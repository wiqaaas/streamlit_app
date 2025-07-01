# streamlit_app_1.py
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from datetime import date

from sheets import load_data
from example_posts import example_posts_json
from openai_client import chat_conversation
from utils import chunk_json

# ─── Config & env ────────────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
TOKEN_THRESHOLD  = 900_000  # effectively disable summarization

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Load & chunk data ────────────────────────────────────────────
ele_chunks, sch_chunks    = load_data(ELEARNING_SOURCE, SCHEDULE_SOURCE)
example_chunks            = chunk_json(example_posts_json)

# ─── Session‐state init ───────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history     = []   # only user & assistant turns
    st.session_state.last_reply  = ""
    st.session_state.clear_input = False

# Clear input before widget creation
if st.session_state.clear_input:
    st.session_state.user_input   = ""
    st.session_state.clear_input  = False

# ─── Page UI ─────────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (single-send + context checkbox)")
st.write("Toggle “Include context” to add schedule & e-learning data, then Send.")

# Checkbox to include or skip context injection
include_context = st.checkbox("Include schedule & e-learning context", value=True)

# Always-visible text area, seeded from session_state
user_input = st.text_area(
    "Your message",
    value=st.session_state.user_input if "user_input" in st.session_state else "",
    key="user_input",
    height=150
)

# Send button
if st.button("🚀 Send") and user_input.strip():
    # 1) Build system messages
    messages = [
        {"role":"system","content":"You are PoloGPT, an expert polo-social-media strategist. You output JSON posts with keys Platform, Topic, Content."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]
    # 2) Optionally inject schedule & e-learning context
    if include_context:
        for c in sch_chunks:
            messages.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            messages.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})
    # 3) Always inject example-posts
    for c in example_chunks:
        messages.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})
    # 4) Append the entire prior history of user/assistant
    messages.extend(st.session_state.history)
    # 5) Add the new user turn
    messages.append({"role":"user","content":user_input})

    # 6) Call GPT
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            messages,
            model="gpt-4.1-mini",
            token_threshold=TOKEN_THRESHOLD
        )

    # 7) Record into history
    st.session_state.history.append({"role":"user","content":user_input})
    st.session_state.history.append({"role":"assistant","content":reply})
    st.session_state.last_reply  = reply

    # 8) Clear the input next run
    st.session_state.clear_input = True

# Display only the last assistant reply
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
