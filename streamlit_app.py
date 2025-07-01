import streamlit as st
import json
from datetime import date

from sheets import load_sheet
from openai_client import get_completion
from utils import chunk_json

# ——— CONFIGURATION ———
ELEARNING_URL = os.getenv("ELEARNING_SHEET_URL")
SCHEDULE_URL  = os.getenv("SCHEDULE_SHEET_URL")

ELEARNING_COLS = [
    "Release Date", "Link to page", "LmsCourse", "LmsContributor",
    "Learning Path - Player Introductory", "Learning Path - Player Beginner",
    "Learning Path - Player Intermediate", "Learning Path - Player Advanced",
    "Learning Path - Coach Level 1", "Learning Path - Coach Level 2",
    "Learning Path - Coach Level 3", "Learning Path - Coach Level 4",
    "Learning Path - Umpire Level 1", "Learning Path - Umpire Level 2",
    "Learning Path - Umpire Level 3"
]
SCHEDULE_COLS = [
    "Release Date", "Publicly Available on front end website",
    "Link on Website for Social Media", "Type / Template", "Article Name",
    "Club", "Tournament", "Handicap", "Category 3", "Category 4",
    "Thumbnail", "Video Highlight"
]

# ——— LOAD DATA ———
@st.cache_data
def load_data():
    df_ele = load_sheet(ELEARNING_URL, "Pathway", ELEARNING_COLS)
    df_sch = load_sheet(SCHEDULE_URL,  "Article Schedule", SCHEDULE_COLS)
    # serialize and chunk once
    ele_json = json.dumps(df_ele.to_dict(orient="records"), ensure_ascii=False)
    sch_json = json.dumps(df_sch.to_dict(orient="records"), ensure_ascii=False)
    return chunk_json(ele_json), chunk_json(sch_json)

ele_chunks, sch_chunks = load_data()

# ——— UI ———
st.title("🏇 PoloGPT Chatbot")
st.write("Enter your prompt and I’ll weave in your schedule & e-learning data.")

user_prompt = st.text_area("Your prompt", height=150)
if st.button("Send"):
    messages = [
        {"role": "system", "content":
            "You are PoloGPT, an expert polo‐social‐media strategist."
        }
    ]

    # inject data
    # for c in sch_chunks:
    #     messages.append({"role": "system", "content": f"<SCHEDULE_DATA>\n{c}"})
    # for c in ele_chunks:
    #     messages.append({"role": "system", "content": f"<ELEARNING_DATA>\n{c}"})

    # date context + user prompt
    today_str = date.today().strftime("%B %d, %Y")
    messages.append({"role": "system", "content": f"Today is {today_str}."})
    messages.append({"role": "user",   "content": user_prompt})

    with st.spinner("Thinking…"):
        answer = get_completion(messages)
    st.markdown("**PoloGPT says:**")
    st.write(answer)
