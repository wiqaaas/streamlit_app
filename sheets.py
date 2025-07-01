import os
import gspread
from gspread_dataframe import get_as_dataframe
from dotenv import load_dotenv

load_dotenv()

def load_sheet(sheet_url: str, ws_name: str, cols: list):
    """
    Authenticate via service_account.json, open the given sheet URL + worksheet name,
    return a filtered pandas DataFrame.
    """
    gc = gspread.service_account(filename="service_account.json")
    sh = gc.open_by_url(sheet_url)
    ws = sh.worksheet(ws_name)
    df = get_as_dataframe(ws)
    return df[cols]
