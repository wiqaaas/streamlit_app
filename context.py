# context.py
from datetime import date
from utils import chunk_json
from sheets import load_data
import prompts

from config import (
    ELEARNING_SOURCE, SCHEDULE_SOURCE, MATCHES_SOURCE,
    USE_CONTEXT, USE_EXAMPLES
)

def init_messages():
    # load & chunk
    ele_chunks, sch_chunks, match_chunks = load_data(
        ELEARNING_SOURCE, SCHEDULE_SOURCE, MATCHES_SOURCE
    )
    example_chunks = chunk_json(__import__('example_posts').example_posts_json)
    all_matches   = "\n".join(match_chunks)

    # base system prompts
    msgs = [
        {"role":"system","content":prompts.system_prompt},
        {"role":"system","content":f"Today is {date.today():%Y-%m-%d}."}
    ]

    # optional context
    if USE_CONTEXT:
        for c in sch_chunks:
            msgs.append({"role":"system","content":f"<SCHEDULE_DATA>\n{c}"})
        for c in ele_chunks:
            msgs.append({"role":"system","content":f"<ELEARNING_DATA>\n{c}"})
    if USE_EXAMPLES:
        for c in example_chunks:
            msgs.append({"role":"system","content":f"<EXAMPLE_POSTS>\n{c}"})

    # next matches as a user-turn
    payload = "\n\n".join([
        prompts.prompt_text,
        "<NEXT_MATCHES_JSON>",
        all_matches,
        "</NEXT_MATCHES_JSON>"
    ])
    msgs.append({"role":"user","content": payload})

    return msgs
