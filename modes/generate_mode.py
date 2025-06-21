# modes/generate_mode.py
import streamlit as st
from config import TAB_LABELS
from utils import generate_dummy_response

# Default Lesson copy
DEFAULT_LESSON_TEXT = """
💥 **POWER. PRECISION. POLO.**  
Ever wonder how top players unleash explosive power in every swing? 🎯  

🎬 In this exclusive Professional Insight, James Beim breaks down how to generate serious strength — not just with muscle, but with momentum, technique, and timing.  

⚡ Perfect for beginners building their foundations and intermediates ready to level up their control.  

⛳ Don’t just swing harder — swing smarter.  

📲 Train smarter today. Watch now.  

#PoloTraining #JamesBeim #PoloSwingTechnique
"""

def run_generate_mode():
    st.header("⚙️ Generate Mode")

    # same four tabs as Chat mode
    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            key_base = label.replace(" ", "_").lower()
            inp_key  = f"gen_input_{key_base}"
            btn_key  = f"gen_button_{key_base}"

            # Show default lesson copy if this is the Lesson tab
            if label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)

            # user input
            prompt = st.text_input(f"Enter something to generate for “{label}”:",
                                   key=inp_key)

            # generate button
            if st.button("Generate Response", key=btn_key):
                if prompt:
                    st.write(generate_dummy_response(prompt))
                else:
                    st.warning("Please type a prompt above.")
