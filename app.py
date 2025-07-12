import streamlit as st
from config import TOKEN_THRESHOLD
from context import init_messages
from ui.chat_ui import chat_interface
from ui.sheet_ui import sheet_interface

# Initialize session state once
if "messages" not in st.session_state:
    st.session_state.messages   = init_messages()
    st.session_state.processing = False

    # Send initial payload and store assistant’s reply
    st.session_state.processing = True
    with st.spinner("PoloGPT is thinking…"):
        # this also appends the assistant reply into messages
        from chat_flow import ask_model
        first = ask_model(st.session_state.messages, user_message=None, token_threshold=TOKEN_THRESHOLD)
    st.session_state.last_reply = first
    st.session_state.processing = False

# 1) Chat box (no reply shown here)
chat_interface(st.session_state.messages, token_threshold=TOKEN_THRESHOLD)

# 2) Sheet editor / JSON view for the last_reply
if st.session_state.get("last_reply"):
    sheet_interface(st.session_state.last_reply)
