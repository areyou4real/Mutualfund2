import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

st.set_page_config(page_title="Mutual Fund Allocator", layout="centered")
st.title("📊 Mutual Fund Allocation Analyzer")

uploaded_files = st.file_uploader(
    "Upload one or more Excel files",
    type=["xlsx"],
    accept_multiple_files=True,
    help="Upload mutual fund files in .xlsx format"
)

results = {}

if uploaded_files:
    with st.spinner("Processing uploaded files..."):
        for file in uploaded_files:
            fund_name = file.name
            processor = get_processor(fund_name)

            if processor is None:
                results[fund_name] = f"❌ No processor found for {fund_name}"
                continue

            try:
                file_bytes = file.read()
                df = processor(file_bytes)

                if df is not None and not df.empty:
                    results[fund_name] = df
                else:
                    results[fund_name] = f"❌ No data extracted from {fund_name}"
            except Exception as e:
                results[fund_name] = f"❌ Error processing {fund_name}: {str(e)}"

    st.markdown("---")
    st.header("Results")

    valid_results = {k: v for k, v in results.items() if isinstance(v, pd.DataFrame)}
    invalid_results = {k: v for k, v in results.items() if not isinstance(v, pd.DataFrame)}

    for name, err in invalid_results.items():
        st.error(f"{name}: {err}")

    for name, df in valid_results.items():
        with st.expander(f"📄 {name}"):
            st.dataframe(df)

    if valid_results:
        st.markdown("---")
        st.subheader("📥 Download Consolidated Output")

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for name, df in valid_results.items():
                sheet_name = name.split(".")[0][:31].replace("/", "_").replace("\\", "_")
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)

        st.download_button(
            label="📁 Download Allocation_Output.xlsx",
            data=output,
            file_name="Allocation_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.info("Upload mutual fund Excel files to begin analysis.")
