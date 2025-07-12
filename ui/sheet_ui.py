# ui/sheet_ui.py
import json
import pandas as pd
import streamlit as st
from sheet_client import get_worksheet, fetch_df, append_rows

def sheet_interface(last_reply):
    # parse JSON
    try:
        loaded = json.loads(last_reply)
        parse_err = None
    except Exception as e:
        loaded = None
        parse_err = str(e)

    df = None; norm_err = None
    if isinstance(loaded, list):
        try:
            df = pd.json_normalize(loaded)
        except Exception as e:
            norm_err = str(e)

    if parse_err:
        st.subheader("⚠️ Invalid JSON")
        st.error(parse_err)
        st.code(last_reply)
        edited = None

    elif df is not None:
        st.subheader("1) Review & Edit Your Data")
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    else:
        st.subheader("⚠️ Could not normalize")
        if norm_err: st.error(norm_err)
        st.markdown("`" + str(loaded) + "`")
        edited = None

    if st.button("Send to Google Sheet"):
        ws = get_worksheet()
        sheet_df = fetch_df(ws)
        headers = sheet_df.columns.tolist()

        if df is not None:
            rows = (
                edited.reindex(columns=headers, fill_value="")
                      .fillna("").values.tolist()
            )
        elif isinstance(loaded, list):
            rows = [[str(item)] for item in loaded]
            headers = [headers[0]]
        else:
            rows = [[last_reply]]
            headers = [headers[0]]

        append_rows(ws, rows)
        st.success(f"🎉 Appended {len(rows)} row(s)!")
