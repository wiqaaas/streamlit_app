# sheets.py
import gspread
from gspread_dataframe import get_as_dataframe
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

def load_sheet(url: str, ws_name: str, cols: list):
    # build the absolute path to service_account.json
    key_path = Path(__file__).parent / "service_account.json"
    if not key_path.exists():
        raise FileNotFoundError(f"Could not find {key_path}")
    gc = gspread.service_account(filename=str(key_path))
    sh = gc.open_by_url(url)
    ws = sh.worksheet(ws_name)
    df = get_as_dataframe(ws)
    return df[cols]
