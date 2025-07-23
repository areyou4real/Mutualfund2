import streamlit as st
import pandas as pd
import os
from utils.file_router import get_processor

st.set_page_config(
    page_title="Mutual Fund Allocator",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

st.markdown("""
    <style>
        body { background-color: #121212; color: white; }
        .reportview-container { background-color: #121212; color: white; }
        .sidebar .sidebar-content { background-color: #1e1e1e; }
        .stButton>button { color: white; background-color: #2e2e2e; border: none; }
        .stDownloadButton>button { color: white; background-color: #2e2e2e; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Mutual Fund Category Allocator")

uploaded_files = st.file_uploader("Upload Mutual Fund Files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Processing files..."):
        writer = pd.ExcelWriter("Allocation_Output.xlsx", engine="openpyxl")

        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name

            try:
                processor = get_processor(filename)
                df = processor(file_bytes)
                sheet_name = os.path.splitext(filename)[0][:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                st.subheader(f"Results for: {filename}")
                st.dataframe(df.style.format("{:.2f}"))

            except Exception as e:
                st.error(f"❌ Error processing {filename}: {str(e)}")

        writer.close()

        with open("Allocation_Output.xlsx", "rb") as f:
            st.download_button(
                label="📥 Download All Results",
                data=f,
                file_name="Allocation_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
