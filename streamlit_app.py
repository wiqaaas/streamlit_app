import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from datetime import date

from sheets import load_data
from example_posts import example_posts_json
from openai_client import chat_conversation
from utils import chunk_json

import prompts

# ─── Load env & config ────────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
MATCHES_SOURCE   = os.getenv("MATCHES_SOURCE")
USE_CONTEXT      = False
USE_EXAMPLES     = True 
TOKEN_THRESHOLD  = 900_000  # 900k tokens for gpt-4.1-mini

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE or not MATCHES_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE, SCHEDULE_SOURCE, and MATCHES_SOURCE in .env")
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

# ─── Load & chunk sheets & matches ─────────────────────────────────
ele_chunks, sch_chunks, match_chunks = load_data(
    ELEARNING_SOURCE,
    SCHEDULE_SOURCE,
    MATCHES_SOURCE
)
example_chunks = chunk_json(example_posts_json)

# ─── Session‐state init ───────────────────────────────────────────
if "messages" not in st.session_state:
    # 1) Base system prompts
    base = [
        {"role":"system","content":prompts.system_prompt},
        {"role":"system","content":f"Today is {date.today():%Y-%m-%d}."}
    ]

    # 2) Optionally inject schedule and e-learning
    if USE_CONTEXT:
        for c in sch_chunks:
            base.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            base.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})

    # 3) Optionally inject example posts
    if USE_EXAMPLES:
        for c in example_chunks:
            base.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})

    st.session_state.messages   = base
    st.session_state.processing = False
    st.session_state.last_reply = None

    # ─── Automatic first user‐prompt ───────────────────────────────
   all_matches_json = "\n".join(match_chunks) 
    initial_payload = (
        prompts.prompt_text
        + "\n\n<NEXT_MATCHES_JSON>\n"
        + all_matches_json
        + "\n</NEXT_MATCHES_JSON>"
    )
    st.session_state.messages.append({"role": "user", "content": initial_payload})

    # call the model and record its reply
    with st.spinner("PoloGPT is thinking…"):
        first_reply = chat_conversation(
            st.session_state.messages,
            model="gpt-4.1-mini",
            token_threshold=TOKEN_THRESHOLD
        )
    st.session_state.messages.append({"role": "assistant", "content": first_reply})
    st.session_state.last_reply = first_reply
    st.session_state.processing = False

# ─── UI ────────────────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot")
st.write("Type your message ...")

# bind the textarea to session_state so it persists
user_input = st.text_area(
    "Your message", 
    height=150, 
    key="input"
)

# disable while processing
send = st.button(
    "🚀 Send", 
    disabled=st.session_state.processing
)

# ─── On Send ───────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.processing = True
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            st.session_state.messages + [{"role":"user","content":user_input}],
            model="gpt-4.1-mini",
            token_threshold=TOKEN_THRESHOLD
        )
    # record
    st.session_state.messages.append({"role":"user","content":user_input})
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.last_reply = reply
    st.session_state.processing = False

# ─── Always show last reply ────────────────────────────────────────
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
