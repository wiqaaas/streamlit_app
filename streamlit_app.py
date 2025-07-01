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
USE_CONTEXT      = os.getenv("USE_CONTEXT", "false").lower() in ("1","true","yes")

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

# ─── Load & chunk JSON data ───────────────────────────────────────
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

    # store in session
    st.session_state.base_messages    = base
    st.session_state.ad_messages      = list(base)
    st.session_state.content_messages = list(base)
    st.session_state.has_sent         = False
    st.session_state.last_reply       = ""

# ─── Helper to append and get reply ───────────────────────────────
def send_to(messages_list, prompt: str):
    messages_list.append({"role":"user","content":prompt})
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(
            messages_list,
            model="gpt-4.1-mini",
            token_threshold=1000
        )
    messages_list.append({"role":"assistant","content":reply})
    return reply

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Type your message. After first Send, you get Modify Ad / Modify Content sessions.")

# always-visible text area
message = st.text_area("Your message", height=150, key="msg")

# placeholder for buttons
action_ph = st.empty()

# ─── Initial Send stage ──────────────────────────────────────────
if not st.session_state.has_sent:
    with action_ph.container():
        if st.button("🚀 Send") and message.strip():
            # 1) send to base_messages
            reply = send_to(st.session_state.base_messages, message.strip())
            st.session_state.last_reply = reply

            # 2) seed both ad_messages & content_messages
            st.session_state.ad_messages.append({"role":"user","content":message.strip()})
            st.session_state.ad_messages.append({"role":"assistant","content":reply})
            st.session_state.content_messages.append({"role":"user","content":message.strip()})
            st.session_state.content_messages.append({"role":"assistant","content":reply})

            # 3) flip flag
            st.session_state.has_sent = True

    # show initial reply
    if st.session_state.last_reply:
        st.markdown("**PoloGPT:**")
        st.write(st.session_state.last_reply)

# ─── Modify stage ─────────────────────────────────────────────────
else:
    with action_ph.container():
        col1, col2 = st.columns(2)
        # Modify Ad thread
        if col1.button("✏️ Modify Ad") and message.strip():
            reply = send_to(st.session_state.ad_messages, message.strip())
            st.session_state.last_reply = reply
        # Modify Content thread
        if col2.button("🖋️ Modify Content") and message.strip():
            reply = send_to(st.session_state.content_messages, message.strip())
            st.session_state.last_reply = reply

    # display only the immediate follow-up reply
    if st.session_state.last_reply:
        st.markdown("**PoloGPT:**")
        st.write(st.session_state.last_reply)
