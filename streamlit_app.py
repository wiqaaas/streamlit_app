import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import date

from sheets import load_sheet
from openai_client import chat_conversation
from utils import chunk_json

# ─── Load environment variables ───────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Button styling ────────────────────────────────────────────────
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

# ─── Columns config ───────────────────────────────────────────────
ELEARNING_COLS = [
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

# ─── Load & chunk data ────────────────────────────────────────────
@st.cache_data
def load_data():
    df_ele = load_sheet(ELEARNING_SOURCE, ELEARNING_COLS)
    df_sch = load_sheet(SCHEDULE_SOURCE,  SCHEDULE_COLS)
    ele_json = json.dumps(df_ele.to_dict("records"), ensure_ascii=False)
    sch_json = json.dumps(df_sch.to_dict("records"), ensure_ascii=False)
    return chunk_json(ele_json), chunk_json(sch_json)

ele_chunks, sch_chunks = load_data()

# ─── Session-state init ───────────────────────────────────────────
if "messages" not in st.session_state:
    # system prompt + optional context
    st.session_state.messages = [
        {"role": "system", "content":
            "You are PoloGPT, an expert polo‐social‐media strategist."
        }
    ]
    # ── chunk-data injection commented out ────────────────────────
    # for c in sch_chunks:
    #     st.session_state.messages.append(
    #         {"role": "system", "content": f"<SCHEDULE_DATA>\n{c}"}
    #     )
    # for c in ele_chunks:
    #     st.session_state.messages.append(
    #         {"role": "system", "content": f"<ELEARNING_DATA>\n{c}"}
    #     )

    # date context
    today_str = date.today().strftime("%B %d, %Y")
    st.session_state.messages.append(
        {"role": "system", "content": f"Today is {today_str}."}
    )

    # chat history & input state
    st.session_state.history     = []
    st.session_state.user_input  = ""
    st.session_state.clear_input = False

# ─── Handle input-clearing flag ───────────────────────────────────
if st.session_state.clear_input:
    st.session_state.user_input  = ""
    st.session_state.clear_input = False

# ─── UI ──────────────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Weave in your schedule & e-learning data — continue the convo below.")

# render history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**PoloGPT:** {msg['content']}")

# modify buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("✏️ Modify Ad"):
        st.session_state.user_input = "Please modify the ad based on the above."
with col2:
    if st.button("🖋️ Modify Content"):
        st.session_state.user_input = "Please modify the content based on the above."

# chat input
user_text = st.text_area(
    "Your message",
    value=st.session_state.user_input,
    key="user_input",
    height=150
)

# send
if st.button("🚀 Send") and user_text.strip():
    # append user
    st.session_state.messages.append({"role": "user",    "content": user_text})
    st.session_state.history.append( {"role": "user",    "content": user_text})

    # call GPT
    with st.spinner("PoloGPT is thinking…"):
        reply = chat_conversation(st.session_state.messages, model="gpt-4.1-mini")

    # append assistant
    st.session_state.messages.append({"role": "assistant","content": reply})
    st.session_state.history.append( {"role": "assistant","content": reply})

    # set clear flag (next run clears input)
    st.session_state.clear_input = True
