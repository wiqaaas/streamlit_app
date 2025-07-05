import json
import pandas as pd
from pathlib import Path
from utils import chunk_json

def load_data(elearning_source: str, schedule_source: str):
    """
    Load JSON files dumped from Colab into DataFrames,
    convert to JSON strings, and chunk them.
    """

    def load_json(path: str) -> pd.DataFrame:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return pd.DataFrame(data)

    # Load both DataFrames
    df_ele = load_json(elearning_source)
    df_sch = load_json(schedule_source)

    # Convert each DataFrame back to JSON string
    ele_json = df_ele.to_json(orient="records", force_ascii=False, indent=2)
    sch_json = df_sch.to_json(orient="records", force_ascii=False, indent=2)

    # Chunk each JSON string if desired
    ele_chunks = chunk_json(ele_json)
    sch_chunks = chunk_json(sch_json)

    return ele_chunks, sch_chunks

