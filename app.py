import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

st.set_page_config(page_title="🧾 Mutual Fund Allocator", layout="centered", page_icon="🧾")

# --- Title and Info ---
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00adb5;
        text-align: center;
        margin-top: 10px;
    }
    .sub-info {
        font-size: 1rem;
        color: #e0e0e0;
        text-align: center;
        margin-bottom: 30px;
    }
    .upload-box .stFileUploader label {
        color: #eeeeee;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧾 Mutual Fund Allocation Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-info">Upload one or more mutual fund Excel files below. We will automatically detect allocations and summarize them for you.</div>', unsafe_allow_html=True)

# --- File Uploader ---
st.markdown("---")
st.markdown("### 📤 Upload your Excel files")
uploaded_files = st.file_uploader("", type=["xlsx"], accept_multiple_files=True, key="file_uploader")

# --- Results Section ---
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
                sheet_name = file_name.split(".")[0][:31]  # Excel sheet name max = 31 chars
                st.markdown(f"#### 📊 {sheet_name.title()} Summary")
                st.dataframe(df, use_container_width=True)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)
        st.markdown("### 📥 Download Processed File")
        st.download_button("Download Excel File", output, file_name="MutualFund_Summary.xlsx", use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; font-size: 0.9rem; color: #999;">
        Made with ❤️ using Streamlit  
        Designed for effortless mutual fund analysis.
    </div>
""", unsafe_allow_html=True)
