# app.py
import streamlit as st
from config import TOKEN_THRESHOLD
from context import init_messages
from ui.chat_ui import chat_interface
from ui.sheet_ui import sheet_interface

# initialize session state
if "messages" not in st.session_state:
    st.session_state.messages   = init_messages()
    st.session_state.processing = False
    st.session_state.last_reply = st.session_state.messages[-1]["content"]

# Chat UI
chat_interface(st.session_state.messages, token_threshold=TOKEN_THRESHOLD)

# Sheet UI
if st.session_state.last_reply:
    sheet_interface(st.session_state.last_reply)
