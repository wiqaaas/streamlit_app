import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load .env if you need it here (not strictly required)
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
