import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from datetime import date

from sheets import load_data
from example_posts import example_posts_json
from openai_client import chat_conversation
from utils import chunk_json

# ─── Load env & config ────────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
USE_CONTEXT      = True
USE_EXAMPLES     = True 
TOKEN_THRESHOLD  = 900_000  # 900k tokens for gpt-4.1-mini

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Button styling ────────────────────────────────────────────────
st.markdown("""
<style>
button[data-baseweb="button"] {
  background-color: #1e81b0;
  color: white;
  border-radius: 8px;
  padding: 0.6em 1.2em;
  margin: 0.25em;
  font-size: 1em;
}
button[data-baseweb="button"]:hover {
  background-color: #18658f;
}
</style>
""", unsafe_allow_html=True)

# ─── Load & chunk sheets ──────────────────────────────────────────
ele_chunks, sch_chunks = load_data(ELEARNING_SOURCE, SCHEDULE_SOURCE)
example_chunks   = chunk_json(example_posts_json)

# ─── Session‐state initialization ─────────────────────────────────
if "messages" not in st.session_state:
    base = [
        {"role":"system","content":"You are PoloGPT, an expert polo‐social‐media strategist. You know how to craft posts in JSON with keys Platform, Topic, Content."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]
    if USE_CONTEXT:
        for c in sch_chunks:
            base.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            base.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})
    if USE_EXAMPLES:
        for c in example_chunks:
            base.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})
    st.session_state.messages   = base
    st.session_state.processing = False

# ─── Helper to send & record ───────────────────────────────────────
def send_message(prompt: str) -> str:
    history = st.session_state.messages
    return chat_conversation(
        history + [{"role":"user","content":prompt}],
        model="gpt-4.1-mini",
        token_threshold=TOKEN_THRESHOLD
    )

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Type your message and hit Send. Each send updates the conversation.")

# ── Use a form that clears on submit ─────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("Your message", height=150, key="input")
    submit = st.form_submit_button(
        "🚀 Send",
        disabled=st.session_state.processing
    )

if submit and user_input.strip():
    # mark processing, disable button on rerun
    st.session_state.processing = True

    # show spinner while waiting
    with st.spinner("PoloGPT is thinking…"):
        reply = send_message(user_input.strip())

    # record the turn
    st.session_state.messages.append({"role":"user","content":user_input})
    st.session_state.messages.append({"role":"assistant","content":reply})

    # done processing
    st.session_state.processing = False

    # display reply
    st.markdown("**PoloGPT:**")
    st.write(reply)
