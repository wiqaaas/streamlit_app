# sheets.py
import gspread
from gspread_dataframe import get_as_dataframe
from pathlib import Path
from dotenv import load_dotenv

# load your .env (for the sheet URLs, if you need them here)
load_dotenv()

# point to service_account.json sitting next to this file
BASE = Path(__file__).parent
KEY_FILE = BASE / "service_account.json"

if not KEY_FILE.is_file():
    raise FileNotFoundError(f"Couldn’t find your key at {KEY_FILE}")

def load_sheet(url: str, ws_name: str, cols: list):
    """
    Authenticate with the service account key sitting next to this file,
    then open the sheet & return just the columns you asked for.
    """
    gc = gspread.service_account(filename=str(KEY_FILE))
    sh = gc.open_by_url(url)
    ws = sh.worksheet(ws_name)
    df = get_as_dataframe(ws)
    return df[cols]
