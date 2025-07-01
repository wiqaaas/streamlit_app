import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import date

from sheets import load_sheet
from openai_client import chat_conversation
from utils import chunk_json

# ─── Load env & validate ──────────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")
ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Button CSS ──────────────────────────────────────────────────
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# ─── Load & chunk your JSON sheets (cached) ───────────────────────
@st.cache_data
def load_data():
    ELEARNING_COLS = [  # same as before
        "Release Date","Link to page","LmsCourse","LmsContributor",
        "Learning Path - Player Introductory","Learning Path - Player Beginner",
        "Learning Path - Player Intermediate","Learning Path - Player Advanced",
        "Learning Path - Coach Level 1","Learning Path - Coach Level 2",
        "Learning Path - Coach Level 3","Learning Path - Coach Level 4",
        "Learning Path - Umpire Level 1","Learning Path - Umpire Level 2",
        "Learning Path - Umpire Level 3"
    ]
    SCHEDULE_COLS = [
        "Release Date","Publicly Available on front end website",
        "Link on Website for Social Media","Type / Template","Article Name",
        "Club","Tournament","Handicap","Category 3","Category 4",
        "Thumbnail","Video Highlight"
    ]
    df_ele = load_sheet(ELEARNING_SOURCE, ELEARNING_COLS)
    df_sch = load_sheet(SCHEDULE_SOURCE,  SCHEDULE_COLS)
    ele_json = json.dumps(df_ele.to_dict("records"), ensure_ascii=False)
    sch_json = json.dumps(df_sch.to_dict("records"), ensure_ascii=False)
    return chunk_json(ele_json), chunk_json(sch_json)

ele_chunks, sch_chunks = load_data()

# ─── Initialize session state once ────────────────────────────────
if "messages" not in st.session_state:
    # Base system prompts
    st.session_state.messages = [
        {"role":"system","content":"You are PoloGPT, an expert polo‐social‐media strategist."},
        {"role":"system","content":f"Today is {date.today():%B %d, %Y}."}
    ]
    # ── Context injection, uncomment if needed ──────────────────────
    # for c in sch_chunks:
    #     st.session_state.messages.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
    # for c in ele_chunks:
    #     st.session_state.messages.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})

    st.session_state.has_sent   = False   # hide/replace Send after first click
    st.session_state.last_reply = ""      # store immediate reply

# ─── Build the UI ─────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Enter your prompt; after the first send, only Modify buttons will appear.")

# ─── Initial send stage ──────────────────────────────────────────
if not st.session_state.has_sent:
    with st.form("send_form", clear_on_submit=True):
        user_text = st.text_area("Your message", height=150)
        send = st.form_submit_button("🚀 Send")
    if send and user_text.strip():
        # Record user message
        st.session_state.messages.append({"role":"user","content":user_text})
        # Call GPT (handles summarization internally)
        with st.spinner("PoloGPT is thinking…"):
            reply = chat_conversation(
                st.session_state.messages,
                model="gpt-4.1-mini",
                token_threshold=1000
            )
        # Record assistant reply
        st.session_state.messages.append({"role":"assistant","content":reply})
        st.session_state.last_reply  = reply
        st.session_state.has_sent    = True

# ─── Modify stage ─────────────────────────────────────────────────
else:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Modify Ad"):
            prompt = "Please modify the ad based on the above."
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.spinner("PoloGPT is thinking…"):
                reply = chat_conversation(
                    st.session_state.messages,
                    model="gpt-4.1-mini",
                    token_threshold=1000
                )
            st.session_state.messages.append({"role":"assistant","content":reply})
            st.session_state.last_reply = reply
    with col2:
        if st.button("🖋️ Modify Content"):
            prompt = "Please modify the content based on the above."
            st.session_state.messages.append({"role":"user","content":prompt})
            with st.spinner("PoloGPT is thinking…"):
                reply = chat_conversation(
                    st.session_state.messages,
                    model="gpt-4.1-mini",
                    token_threshold=1000
                )
            st.session_state.messages.append({"role":"assistant","content":reply})
            st.session_state.last_reply = reply

# ─── Display only the immediate assistant reply ───────────────────
if st.session_state.last_reply:
    st.markdown("**PoloGPT:**")
    st.write(st.session_state.last_reply)
