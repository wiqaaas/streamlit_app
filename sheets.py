import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from utils import chunk_json

# Load .env so we can point to your JSON dumps (paths in ELEARNING_SOURCE, SCHEDULE_SOURCE)
BASE = Path(__file__).parent
load_dotenv(dotenv_path=BASE / ".env")

def load_sheet(source: str, cols: list) -> pd.DataFrame:
    """
    Load a local JSON file (dumped from Colab) into a DataFrame,
    then filter to the requested columns.
    """
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"No such file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    df = pd.DataFrame(data)
    missing = set(cols) - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns in {path.name}: {missing}")
    return df[cols]

# Define which columns we're pulling
ELEARNING_COLS = [
    "Release Date","Link to page","LmsCourse","LmsContributor",
    "Learning Path - Player Introductory","Learning Path - Player Beginner",
    "Learning Path - Player Intermediate","Learning Path - Player Advanced",
    "Learning Path - Coach Level 1","Learning Path - Coach Level 2",
    "Learning Path - Coach Level 3","Learning Path - Coach Level 4",
    "Learning Path - Umpire Level 1","Learning Path - Umpire Level 2",
    "Learning Path - Umpire Level 3"
]
SCHEDULE_COLS = [
    "Release Date","Publicly Available on front end website",
    "Link on Website for Social Media","Type / Template","Article Name",
    "Club","Tournament","Handicap","Category 3","Category 4",
    "Thumbnail","Video Highlight"
]

def load_data(elearning_source: str, schedule_source: str):
    """
    Loads both sheets via load_sheet, serializes to JSON,
    then chunks them via chunk_json.
    Returns (ele_chunks, sch_chunks).
    """
    df_ele = load_sheet(elearning_source, ELEARNING_COLS)
    df_sch = load_sheet(schedule_source,  SCHEDULE_COLS)
    ele_json = json.dumps(df_ele.to_dict("records"), ensure_ascii=False)
    sch_json = json.dumps(df_sch.to_dict("records"), ensure_ascii=False)
    return chunk_json(ele_json), chunk_json(sch_json)
