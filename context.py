# context.py
from datetime import date
from utils import chunk_json
from sheets import load_data
import prompts

from config import (
    ELEARNING_SOURCE, SCHEDULE_SOURCE, MATCHES_SOURCE,
    USE_CONTEXT, USE_EXAMPLES
)

def init_system_messages():
    """
    Returns:
      - system_msgs: a list of only your system messages
      - match_chunks: the raw chunk list for next-matches JSON
    """
    ele_chunks, sch_chunks, match_chunks = load_data(
        ELEARNING_SOURCE, SCHEDULE_SOURCE, MATCHES_SOURCE
    )
    example_chunks = chunk_json(__import__('example_posts').example_posts_json)

    # 1) Core system prompts
    system_msgs = [
        {"role":"system","content":prompts.system_prompt},
        {"role":"system","content":f"Today is {date.today():%Y-%m-%d}."}
    ]

    # 2) Optionally inject schedule & e-learning
    if USE_CONTEXT:
        for c in sch_chunks:
            system_msgs.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            system_msgs.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})

    # 3) Optionally inject example posts
    if USE_EXAMPLES:
        for c in example_chunks:
            system_msgs.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})

    return system_msgs, match_chunks


def build_initial_user_message(match_chunks: list[str]) -> str:
    """
    Builds the very first user-turn payload,
    embedding prompts.prompt_text + your NEXT_MATCHES_JSON block.
    """
    all_matches = "\n".join(match_chunks)

    return "\n\n".join([
        prompts.prompt_text,
        "<NEXT_MATCHES_JSON>",
        all_matches,
        "</NEXT_MATCHES_JSON>"
    ])
