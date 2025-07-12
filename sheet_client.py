import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# CONFIGURATION
# -----------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDS_PATH = "/content/trial-465018-48d518fd746f.json"
SHEET_ID = "1sJdOnY0J3YpybcgWsIwVWuc-8JzjLxXZ2MHu8KXHqpw"
TAB_NAME = "Sheet-1"

def get_worksheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.worksheet(TAB_NAME)

def fetch_df(worksheet):
    data = worksheet.get_all_values()
    if len(data) > 1:
        return pd.DataFrame(data[1:], columns=data[0])
    else:
        return pd.DataFrame(columns=data[0])

def append_rows(worksheet, rows):
    # rows: list of lists
    worksheet.append_rows(rows)
