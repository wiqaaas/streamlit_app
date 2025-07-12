import json
import pandas as pd
from pathlib import Path
from utils import chunk_json

def load_data(
    elearning_source: str,
    schedule_source: str,
    matches_source: str
):
    """
    Load three JSON files dumped from Colab (e-learning, schedule, next matches)
    into DataFrames, convert to JSON strings, and chunk them.
    Returns (ele_chunks, sch_chunks, match_chunks).
    """

    def load_json(path: str) -> pd.DataFrame:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(data)

    # Load each DataFrame
    df_ele     = load_json(elearning_source)
    df_sch     = load_json(schedule_source)
    df_matches = load_json(matches_source)

    # Convert DataFrames back to pretty JSON strings
    ele_json     = df_ele.to_json(orient="records", force_ascii=False, indent=2)
    sch_json     = df_sch.to_json(orient="records", force_ascii=False, indent=2)
    matches_json = df_matches.to_json(orient="records", force_ascii=False, indent=2)

    # Chunk each JSON string
    ele_chunks     = chunk_json(ele_json)
    sch_chunks     = chunk_json(sch_json)
    match_chunks   = chunk_json(matches_json)

    return ele_chunks, sch_chunks, match_chunks
