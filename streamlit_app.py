import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import date

from sheets import load_data
from openai_client import chat_conversation

# ─── Load env & config ────────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
USE_CONTEXT      = False

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Button styling ───────────────────────────────────────────────
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

# ─── Load & chunk both sheets ─────────────────────────────────────
ele_chunks, sch_chunks = load_data(ELEARNING_SOURCE, SCHEDULE_SOURCE)

# ─── Session‐state initialization ─────────────────────────────────
if "messages" not in st.session_state:
    # Base system prompts
    st.session_state.messages = [
        {"role":"system","content":"You are PoloGPT, an expert polo‐social‐media strategist."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]

    # Conditionally inject context
    if USE_CONTEXT:
        for c in sch_chunks:
            st.session_state.messages.append({
                "role":"system",
                "content": f"<SCHEDULE_DATA>\n{c}"
            })
        for c in ele_chunks:
            st.session_state.messages.append({
                "role":"system",
                "content": f"<ELEARNING_DATA>\n{c}"
            })

    st.session_state.has_sent   = False   # hides Send after first click
    st.session_state.last_reply = ""      # holds latest assistant reply

# ─── Helper to send a prompt and update state ────────────────────
def process_prompt(prompt: str):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            st.session_state.messages,
            model="gpt-4.1-mini",
            token_threshold=1000
        )
    st.session_state.messages.append({"role":"assistant","content":reply})
    st.session_state.last_reply = reply

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Type your message below. After first Send, you get Modify buttons.")

# Always‐visible text area
message = st.text_area("Your message", height=150, key="message_input")

# Placeholder for action buttons
action_ph = st.empty()

# First‐click: show Send
if not st.session_state.has_sent:
    with action_ph.container():
        if st.button("🚀 Send") and message.strip():
            process_prompt(message.strip())
            st.session_state.has_sent = True

# Subsequent: show Modify Ad / Modify Content
else:
    with action_ph.container():
        col1, col2 = st.columns(2)
        if col1.button("✏️ Modify Ad") and message.strip():
            process_prompt(message.strip())
        if col2.button("🖋️ Modify Content") and message.strip():
            process_prompt(message.strip())

# Display only the immediate assistant reply
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
