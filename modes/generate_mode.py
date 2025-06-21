# modes/generate_mode.py
import streamlit as st
from config import TAB_LABELS
from utils import generate_dummy_response

def run_generate_mode():
    st.header("⚙️ Generate Mode")

    # Create the same four tabs as in Chat mode
    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            # Unique keys per tab
            key_base = label.replace(" ", "_").lower()

            # Text input for this tab
            prompt = st.text_input(
                f"Enter something to generate for “{label}”:",
                key=f"gen_input_{key_base}"
            )

            # Generate button for this tab
            if st.button("Generate Response", key=f"gen_button_{key_base}"):
                if prompt:
                    st.write(generate_dummy_response(prompt))
                else:
                    st.warning("Please type a prompt above.")
