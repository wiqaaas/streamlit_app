import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import date
import tiktoken

from sheets import load_sheet
from openai_client import get_completion
from utils import chunk_json

# ─── Load environment variables ────────────────────────────────────
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE        = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE         = os.getenv("SCHEDULE_SOURCE")
MAX_TOKEN_LIMIT         = int(os.getenv("MAX_TOKEN_LIMIT", 10000))
DEFAULT_FALLBACK_MESSAGE = os.getenv(
    "DEFAULT_FALLBACK_MESSAGE",
    "Your request was too long; please shorten it and try again."
)

if not ELEARNING_SOURCE or not SCHEDULE_SOURCE:
    st.error("❌ Please set ELEARNING_SOURCE and SCHEDULE_SOURCE in .env")
    st.stop()

# ─── Constants ───────────────────────────────────────────────────
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

# ─── Load & chunk JSON data ─────────────────────────────────────
@st.cache_data
def load_data():
    df_ele = load_sheet(ELEARNING_SOURCE, ELEARNING_COLS)
    df_sch = load_sheet(SCHEDULE_SOURCE,  SCHEDULE_COLS)
    ele_json = json.dumps(df_ele.to_dict(orient="records"), ensure_ascii=False)
    sch_json = json.dumps(df_sch.to_dict(orient="records"), ensure_ascii=False)
    return chunk_json(ele_json), chunk_json(sch_json)

ele_chunks, sch_chunks = load_data()

# ─── Initialize chat state ───────────────────────────────────────
if "messages" not in st.session_state:
    # System & context injection only once
    st.session_state.messages = [
        {"role": "system", "content":
            "You are PoloGPT, an expert polo-social-media strategist."
        }
    ]
    # for c in sch_chunks:
    #     st.session_state.messages.append(
    #         {"role": "system", "content": f"<SCHEDULE_DATA>\n{c}"}
    #     )
    # for c in ele_chunks:
    #     st.session_state.messages.append(
    #         {"role": "system", "content": f"<ELEARNING_DATA>\n{c}"}
    #     )
    today_str = date.today().strftime("%B %d, %Y")
    st.session_state.messages.append(
        {"role": "system", "content": f"Today is {today_str}."}
    )
    # History for display (excludes system messages)
    st.session_state.history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ─── UI ─────────────────────────────────────────────────────────
st.title("🏇 PoloGPT Chatbot (gpt-4.1-mini)")
st.write("Weave in your schedule & e-learning data — continue the convo below.")

# Display the chat history
for entry in st.session_state.history:
    if entry["role"] == "user":
        st.markdown(f"**You:** {entry['content']}")
    else:
        st.markdown(f"**PoloGPT:** {entry['content']}")

# Input box for next user message
st.text_area(
    "Your message",
    key="user_input",
    height=150
)

# The three action buttons
col1, col2, col3 = st.columns(3)
with col1:
    send_clicked = st.button("Send")
with col2:
    mod_ad = st.button("Modify Ad")
with col3:
    mod_content = st.button("Modify Content")

# If either modify button is clicked, pre-fill the input box
if mod_ad:
    st.session_state.user_input = "Please modify the ad based on the above."
if mod_content:
    st.session_state.user_input = "Please modify the content based on the above."

# When Send is clicked, append and call the API
if send_clicked and st.session_state.user_input.strip():
    user_msg = st.session_state.user_input.strip()

    # Append user message to session
    st.session_state.messages.append({"role": "user", "content": user_msg})
    st.session_state.history.append({"role": "user", "content": user_msg})

    # Count tokens
    try:
        enc = tiktoken.encoding_for_model("gpt-4.1-mini")
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    token_count = sum(len(enc.encode(m["content"])) for m in st.session_state.messages)
    st.write(f"**Token count:** {token_count}")

    # Decide fallback or full convo
    if token_count > MAX_TOKEN_LIMIT:
        st.warning(f"Token count ({token_count}) exceeds the limit of {MAX_TOKEN_LIMIT}.")
        prompt = [
            {"role": "system", "content":
                "You are PoloGPT, an expert polo-social-media strategist."},
            {"role": "user", "content": DEFAULT_FALLBACK_MESSAGE}
        ]
    else:
        prompt = st.session_state.messages

    # Call the API
    with st.spinner("PoloGPT is thinking…"):
        reply = get_completion(prompt, model="gpt-4.1-mini")

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.history.append({"role": "assistant", "content": reply})

    # Clear input box
    st.session_state.user_input = ""

    # Rerun to display updated history
    st.experimental_rerun()
