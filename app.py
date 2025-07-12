# app.py (excerpt)
import streamlit as st
from context import init_system_messages, build_initial_user_message
from chat_flow import ask_model
from ui.chat_ui import chat_interface
from ui.sheet_ui import sheet_interface
from config import TOKEN_THRESHOLD

# ─── One-time setup ────────────────────────────────────────────────
if "messages" not in st.session_state:
    # 1) pull in only the system messages + match_chunks
    system_msgs, match_chunks = init_system_messages()
    st.session_state.messages = system_msgs

    # 2) build your first-thing-to-ask
    initial_payload = build_initial_user_message(match_chunks)

    # 3) send that payload explicitly (user_message is never None!)
    st.session_state.processing = True
    with st.spinner("PoloGPT is thinking…"):
        first_reply = ask_model(
            st.session_state.messages,
            user_message=initial_payload,
            token_threshold=TOKEN_THRESHOLD
        )
    st.session_state.last_reply = first_reply
    st.session_state.processing = False

# ─── The rest of your app ─────────────────────────────────────────
chat_interface(
    history=st.session_state.messages,
    token_threshold=TOKEN_THRESHOLD
)

if st.session_state.get("last_reply"):
    sheet_interface(st.session_state.last_reply)
