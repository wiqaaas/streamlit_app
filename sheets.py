# sheets.py
import os
from pathlib import Path
import gspread
from gspread_dataframe import get_as_dataframe
from dotenv import load_dotenv

# Load your .env if you need sheet URLs or other config
BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

# Pick up the key via env var (standard Google pattern)
KEYFILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", str(BASE / "service_account.json"))
if not Path(KEYFILE).is_file():
    raise FileNotFoundError(f"Couldn’t find service account JSON at {KEYFILE}")

# Create one client for all calls
_gc = gspread.service_account(filename=KEYFILE)

def load_sheet(url: str, ws_name: str, cols: list):
    sh = _gc.open_by_url(url)
    ws = sh.worksheet(ws_name)
    df = get_as_dataframe(ws)
    return df[cols]
