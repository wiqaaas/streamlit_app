# sheets.py
from google.colab import auth
from google.auth import default
import gspread
from gspread_dataframe import get_as_dataframe

# ——— INTERACTIVE AUTH ———
# On first import this will pop up the Google sign-in/consent UI.
auth.authenticate_user()
creds, _ = default()
_gc = gspread.authorize(creds)

def load_sheet(url: str, ws_name: str, cols: list):
    """
    Uses your interactive Google login to open the sheet at `url`,
    pulls worksheet `ws_name`, filters to `cols`, and returns a DataFrame.
    """
    sh = _gc.open_by_url(url)
    ws = sh.worksheet(ws_name)
    df = get_as_dataframe(ws)
    return df[cols]
