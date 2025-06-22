# modes/filter_mode.py
import streamlit as st
import pandas as pd
from config import TAB_LABELS

def run_filter_mode():
    st.header("🔍 Filter Mode")

    # Attempt to load the Excel file once
    try:
        df = pd.read_excel("dummy_data.xlsx")
    except Exception as e:
        st.error(f"Failed to load dummy_data.xlsx: {e}")
        return

    tabs = st.tabs(TAB_LABELS)
    for label, tab in zip(TAB_LABELS, tabs):
        with tab:
            st.subheader(f"📊 Data for {label}")
            st.dataframe(df)

            # Ask for a row index
            idx = st.number_input(
                f"Enter row index (0 to {len(df)-1}) for {label}:",
                min_value=0,
                max_value=len(df)-1,
                step=1,
                key=f"row_idx_{label}"
            )

            if st.button(f"Show row {idx} info", key=f"show_row_{label}"):
                try:
                    row = df.iloc[idx]
                    # Build a single-line description
                    info = "; ".join(f"{col}: {row[col]}" for col in df.columns)
                    st.markdown(f"**Row {idx} data:** {info}")
                except Exception as e:
                    st.error(f"Could not read row {idx}: {e}")
