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
USE_CONTEXT      = os.getenv("USE_CONTEXT", "false").lower() in ("1","true","yes")
USE_EXAMPLES     = True 

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

# ─── Chunk the example-posts JSON ─────────────────────────────────
example_chunks = chunk_json(example_posts_json)

# ─── Session‐state initialization ─────────────────────────────────
if "base_messages" not in st.session_state:
    # 1) Base system prompts
    base = [
        {"role":"system","content":"You are PoloGPT, an expert polo‐social‐media strategist."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]

    # 2) Optionally inject schedule/e‐learning
    if USE_CONTEXT:
        for c in sch_chunks:
            base.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            base.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})

    # 3) Optionally inject example posts
    if USE_EXAMPLES:
        for c in example_chunks:
            base.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})

    # 4) Store separate histories
    st.session_state.base_messages    = base
    st.session_state.ad_messages      = list(base)
    st.session_state.content_messages = list(base)
    st.session_state.has_sent         = False
    st.session_state.last_reply       = ""

# ─── Helper functions ─────────────────────────────────────────────
def initial_send(prompt: str):
    # send on base_messages
    st.session_state.base_messages.append({"role":"user","content":prompt})
    reply = _call_and_record(st.session_state.base_messages, prompt)
    # seed both modify threads
    for hist in (st.session_state.ad_messages, st.session_state.content_messages):
        hist.append({"role":"user","content":prompt})
        hist.append({"role":"assistant","content":reply})
    return reply

def modify_ad(prompt: str):
    # strip out only the example/schedule/e-learning system messages
    history = [
        m for m in st.session_state.ad_messages
        if m["role"]!="system" or not m["content"].startswith(("<SCHEDULE_DATA>","<ELEARNING_DATA>","<EXAMPLE_POSTS>"))
    ]
    return _call_and_record(history, prompt, to_hist=st.session_state.ad_messages)

def modify_content(prompt: str):
    # full history
    return _call_and_record(st.session_state.content_messages, prompt, to_hist=st.session_state.content_messages)

def _call_and_record(history, prompt, to_hist=None):
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(history + [{"role":"user","content":prompt}], model="gpt-4.1-mini", token_threshold=1000)
    # record
    if to_hist is None: to_hist = history
    to_hist.append({"role":"user","content":prompt})
    to_hist.append({"role":"assistant","content":reply})
    return reply

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Type your message. After Send, choose Modify Ad or Modify Content.")

# always-visible input
message = st.text_area("Your message", height=150)

# initial Send
if not st.session_state.has_sent:
    if st.button("🚀 Send") and message.strip():
        st.session_state.last_reply = initial_send(message.strip())
        st.session_state.has_sent   = True

# modify buttons
else:
    col1, col2 = st.columns(2)
    if col1.button("✏️ Modify Ad") and message.strip():
        st.session_state.last_reply = modify_ad(message.strip())
    if col2.button("🖋️ Modify Content") and message.strip():
        st.session_state.last_reply = modify_content(message.strip())

# show only the last reply
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
