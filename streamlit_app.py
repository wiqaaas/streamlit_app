import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from datetime import date

from sheets import load_data
from openai_client import chat_conversation

# ─── Load env & config ────────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
USE_CONTEXT      = os.getenv("USE_CONTEXT", "false").lower() in ("1","true","yes")

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Button CSS ─────────────────────────────────────────────────
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

# ─── Load & chunk JSON data ─────────────────────────────────────
ele_chunks, sch_chunks = load_data(ELEARNING_SOURCE, SCHEDULE_SOURCE)

# ─── Session‐state initialization ─────────────────────────────────
if "base_messages" not in st.session_state:
    # build base system context
    base = [
        {"role":"system","content":"You are PoloGPT, an expert polo‐social‐media strategist."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]
    if USE_CONTEXT:
        for c in sch_chunks:
            base.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            base.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})

    st.session_state.base_messages    = base
    st.session_state.ad_messages      = list(base)
    st.session_state.content_messages = list(base)
    st.session_state.has_sent         = False
    st.session_state.last_reply       = ""

# ─── Helper for Modify Ad (context‐stripped) ─────────────────────
def modify_ad(prompt: str):
    # Keep only base system messages (no <SCHEDULE_DATA> or <ELEARNING_DATA>)
    filtered = [
        m for m in st.session_state.ad_messages
        if not (m["role"]=="system" and
                (m["content"].startswith("<SCHEDULE_DATA>") or
                 m["content"].startswith("<ELEARNING_DATA>")))
    ]
    # Append the new user prompt
    to_send = filtered + [{"role":"user","content":prompt}]
    # Call the model
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            to_send,
            model="gpt-4.1-mini",
            token_threshold=1000
        )
    # Update the ad_messages history (so future Modify Ad runs on cumulative chat)
    st.session_state.ad_messages.append({"role":"user","content":prompt})
    st.session_state.ad_messages.append({"role":"assistant","content":reply})
    return reply

# ─── Helper for Modify Content (full context) ────────────────────
def modify_content(prompt: str):
    # Use the full content_messages (with context)
    st.session_state.content_messages.append({"role":"user","content":prompt})
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            st.session_state.content_messages,
            model="gpt-4.1-mini",
            token_threshold=1000
        )
    st.session_state.content_messages.append({"role":"assistant","content":reply})
    return reply

# ─── Helper for the very first Send (seeds both sessions) ───────
def initial_send(prompt: str):
    # Send to base_messages
    st.session_state.base_messages.append({"role":"user","content":prompt})
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            st.session_state.base_messages,
            model="gpt-4.1-mini",
            token_threshold=1000
        )
    st.session_state.base_messages.append({"role":"assistant","content":reply})
    # Seed both histories with first turn
    for hist in (st.session_state.ad_messages, st.session_state.content_messages):
        hist.append({"role":"user","content":prompt})
        hist.append({"role":"assistant","content":reply})
    return reply

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Type your message. After Send, use the separate Modify buttons.")

# — Always‐visible text area —
message = st.text_area("Your message", height=150, key="msg")

# — Initial Send button (once only) —
if not st.session_state.has_sent:
    if st.button("🚀 Send") and message.strip():
        reply = initial_send(message.strip())
        st.session_state.last_reply = reply
        st.session_state.has_sent   = True

# — Modify buttons (appear immediately on first send) —
else:
    col1, col2 = st.columns(2)
    if col1.button("✏️ Modify Ad") and message.strip():
        reply = modify_ad(message.strip())
        st.session_state.last_reply = reply
    if col2.button("🖋️ Modify Content") and message.strip():
        reply = modify_content(message.strip())
        st.session_state.last_reply = reply

# — Display only the immediate assistant reply —
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
