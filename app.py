import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="🧾 Mutual Fund Allocator",
    page_icon="🧾",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    /* Global Styling */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #00ADB5;
        text-align: center;
        margin-top: 20px;
    }

    .sub-info {
        font-size: 1.1rem;
        color: #b0b0b0;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Section Header */
    .stMarkdown h3 {
        color: #FFD369 !important;
        border-bottom: 2px solid #393E46;
        padding-bottom: 5px;
    }

    /* Upload Box */
    .upload-box .stFileUploader label {
        color: #EEEEEE !important;
        font-weight: 600;
    }

    /* Dataframe */
    .stDataFrame div {
        background-color: #1f1f1f !important;
    }

    /* Download Button */
    .stDownloadButton button {
        background-color: #00ADB5;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
    }

    .stDownloadButton button:hover {
        background-color: #00cfcf;
        transition: 0.3s;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.85rem;
        color: #AAAAAA;
        margin-top: 2rem;
        padding: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title and Subtitle ---
st.markdown('<div class="main-title">🧾 Mutual Fund Allocation Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-info">Upload one or more mutual fund Excel files below. We will automatically detect allocations and summarize them for you.</div>', unsafe_allow_html=True)

# --- File Uploader ---
st.markdown("---")
st.markdown("### 📤 Upload your Excel files")
uploaded_files = st.file_uploader(
    "Select one or more `.xlsx` files",
    type=["xlsx"],
    accept_multiple_files=True,
    key="file_uploader",
    help="Only Excel (.xlsx) files are supported"
)

# --- Processing Section ---
if uploaded_files:
    st.markdown("---")
    st.markdown("### ⚙️ Processing Results")

    file_dict = {file.name: file.read() for file in uploaded_files}
    valid_results = {}
    error_results = {}

    for file_name, file_bytes in file_dict.items():
        try:
            processor = get_processor(file_name)
            result = processor(file_bytes)
            if isinstance(result, pd.DataFrame):
                valid_results[file_name] = result
            else:
                error_results[file_name] = "Processor did not return a DataFrame."
        except Exception as e:
            error_results[file_name] = str(e)

    # --- Display Errors ---
    if error_results:
        st.markdown("---")
        st.error("❌ Errors encountered while processing the following files:")
        for file_name, err in error_results.items():
            st.markdown(f"**{file_name}**: `{err}`")

    # --- Display Valid Results ---
    if valid_results:
        st.markdown("---")
        st.success("✅ Successfully processed the following files:")

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for file_name, df in valid_results.items(): 
                sheet_name = file_name.split(".")[0][:31]
                
                with st.expander(f"📊 {sheet_name.title()} Summary"):
                    st.dataframe(df, use_container_width=True)
                    
                df.to_excel(writer, sheet_name=sheet_name, index=False)


        output.seek(0)
        st.markdown("### 📥 Download Processed File")
        st.download_button(
            label="Download Excel File",
            data=output,
            file_name="MutualFund_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- Footer ---
st.markdown("---")
st.markdown('<div class="footer">Built by Dheer Doshi · All rights reserved · 2025</div>', unsafe_allow_html=True)
