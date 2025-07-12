# ui/chat_ui.py
import streamlit as st

def chat_interface(history, token_threshold):
    st.title("🏇 PoloGPT Chatbot")
    st.write("Type your message ...")

    user_input = st.text_area("Your message", height=150, key="input")
    send = st.button("🚀 Send", disabled=st.session_state.processing)

    if send and user_input.strip():
        st.session_state.processing = True
        from chat_flow import ask_model
        with st.spinner("PoloGPT is thinking…"):
            reply = ask_model(history, user_input.strip(), token_threshold=token_threshold)
        st.session_state.last_reply = reply
        st.session_state.processing = False
