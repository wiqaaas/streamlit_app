# modes/generate_mode.py
import streamlit as st
from config import TAB_LABELS
from utils import generate_dummy_response

# Default Upcoming Match copy
DEFAULT_MATCH_TEXT = """
🇮🇪 **Rivalry reborn on Irish turf.**  
Bunclody Polo Club hosted a fierce face-off last season as Glenpatrick and Tyrone battled under grey skies and roaring crowds. 🍀

🌟 Big tackles, sharp turns, and momentum swings made this a match to remember — and it still sets the tone for rivalries across Ireland Polo.

🎥 We’re revisiting this classic clash as part of our seasonal throwbacks — and spotlighting the players who made it unforgettable.

📊 Follow us for exclusive breakdowns, match recaps, and the next generation of Irish polo drama.

#IrelandPolo #GlenpatrickVsTyrone #PoloThrowback
"""

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

# Default Course copy
DEFAULT_COURSE_TEXT = """
🚨 **Master the art of momentum and positioning.**  
A split-second line change can make or break a play — are you reading it right?  

🎓 In this brand-new course, *“Fergus Gould – Quick Line Change,”* you’ll learn how to anticipate, react, and control the game using expert rule interpretation and real-game strategy.  

📈 Designed for intermediate players and Level 2 coaches aiming to elevate field awareness and teach the game more intelligently.  

💡 Get smarter. Get faster. Play sharper.  

👉 Unlock this lesson and more with your IPA subscription.  

#PoloIQ #QuickLineChange #PoloTactics
"""

# Default Article copy
DEFAULT_ARTICLE_TEXT = """
🏆 **Victory at Cirencester!**  
Kulin Rock storms to glory in The Gerald Balding — delivering a thrilling finale at one of the UK’s most iconic clubs GB  

🔥 It was a match packed with intensity, fast breaks, and bold plays — with standout performances that turned the tide when it mattered most.  

📍 Cirencester Park Polo Club  
📅 May 27, 2024  
🎮 Game Reports Series  

👀 Don’t miss the full match breakdown — stats, standout players, and turning points that defined the game.  

📺 Watch the highlights & read the full report now.  

#PoloUK #GameReport #KulinRockVictory
"""

def run_generate_mode():
    st.header("⚙️ Generate Mode")

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            key_base = label.replace(" ", "_").lower()
            inp_key  = f"gen_input_{key_base}"
            btn_key  = f"gen_button_{key_base}"

            # Show the default promo text for each tab
            if label == "Upcoming Match":
                st.markdown(DEFAULT_MATCH_TEXT)
            elif label == "Lesson":
                st.markdown(DEFAULT_LESSON_TEXT)
            elif label == "Course":
                st.markdown(DEFAULT_COURSE_TEXT)
            elif label == "Article":
                st.markdown(DEFAULT_ARTICLE_TEXT)

            # User input
            prompt = st.text_input(
                f"Enter something to generate for “{label}”:",
                key=inp_key
            )

            # Generate button
            if st.button("Generate Response", key=btn_key):
                if prompt:
                    st.write(generate_dummy_response(prompt))
                else:
                    st.warning("Please type a prompt above.")
