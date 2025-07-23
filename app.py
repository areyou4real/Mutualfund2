import streamlit as st
import pandas as pd
from utils.file_router import route_file

st.set_page_config(page_title="Mutual Fund Processor", layout="centered")
st.title("Mutual Fund Category Extractor")
st.markdown("Upload mutual fund Excel files. The app will process them and generate tagged summaries.")

uploaded_files = st.file_uploader("Upload fund files", type=[".xls", ".xlsx"], accept_multiple_files=True)

if uploaded_files:
    processed_data = {}
    for uploaded_file in uploaded_files:
        fund_name = uploaded_file.name
        st.markdown(f"### Processing: `{fund_name}`")

        processor = route_file(fund_name)
        if processor is None:
            st.error(f"No processor found for file `{fund_name}`. Please ensure the filename contains a recognizable fund name.")
            continue

        try:
            file_bytes = uploaded_file.read()
            df_result = processor(file_bytes)
            processed_data[fund_name] = df_result
            st.dataframe(df_result)
        except Exception as e:
            st.error(f"Error processing `{fund_name}`: {str(e)}")

    if processed_data:
        with st.spinner("Generating Excel file..."):
            output = pd.ExcelWriter("processed_funds.xlsx", engine="openpyxl")
            for fund, df in processed_data.items():
                sheet_name = os.path.splitext(fund)[0][:31]  # Excel sheet names limit
                df.to_excel(output, sheet_name=sheet_name, index=False)
            output.close()

            with open("processed_funds.xlsx", "rb") as f:
                st.download_button(
                    label="Download Combined Excel",
                    data=f,
                    file_name="processed_funds.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
