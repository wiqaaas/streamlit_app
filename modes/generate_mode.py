# modes/generate_mode.py
import streamlit as st
from utils import generate_dummy_response

def run_generate_mode():
    st.header("⚙️ Generate Mode")
    inp = st.text_input("Enter something to generate a dummy response:", key="gen_input")
    if st.button("Generate Response", key="gen_button"):
        if inp:
            st.write(generate_dummy_response(inp))
        else:
            st.warning("Please type a prompt above.")
