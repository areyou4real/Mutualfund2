import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

# --- Streamlit Config ---
st.set_page_config(page_title="🧾 Mutual Fund Allocator", layout="centered", initial_sidebar_state="collapsed")

# --- Custom CSS and Animations ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #101010;
        color: #f1f1f1;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #00FFF5;
        margin-top: 1rem;
        animation: fadeIn 1s ease-in-out;
    }

    .sub-info {
        font-size: 1.1rem;
        text-align: center;
        color: #BBBBBB;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in-out;
    }

    .upload-section, .results-section {
        background-color: #1a1a1a;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.1);
        margin-bottom: 2rem;
    }

    .stDownloadButton button {
        background-color: #00adb5;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: 0.3s ease;
    }

    .stDownloadButton button:hover {
        background-color: #00d8db;
        transform: scale(1.03);
    }

    .footer {
        font-size: 0.85rem;
        text-align: center;
        color: #888888;
        margin-top: 3rem;
        padding-bottom: 1rem;
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="main-title">📊 Mutual Fund Allocation Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-info">Upload Excel files below to automatically detect and summarize mutual fund allocations.</div>', unsafe_allow_html=True)

# --- Upload Section ---
with st.container():
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Excel Files")
    uploaded_files = st.file_uploader(
        "Upload one or more `.xlsx` files",
        type=["xlsx"],
        accept_multiple_files=True,
        key="uploader",
        help="Supported file type: .xlsx"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Processing ---
if uploaded_files:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
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
        st.error("❌ The following files could not be processed:")
        for file_name, error in error_results.items():
            st.markdown(f"- **{file_name}**: `{error}`")

    # --- Display Valid Results ---
    if valid_results:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for file_name, df in valid_results.items():
                sheet_name = file_name.split(".")[0][:31]

                with st.expander(f"📄 {sheet_name.title()} - View Allocation Summary"):
                    st.dataframe(df, use_container_width=True)

                df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)

        st.markdown("### 📥 Download Combined Excel File")
        st.download_button(
            label="Download Summary Excel",
            data=output,
            file_name="MutualFund_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="footer">Built with ❤️ by Dheer Doshi · © 2025</div>', unsafe_allow_html=True)
