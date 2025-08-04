import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

# --- Streamlit Config ---
st.set_page_config(page_title="🧾 Mutual Fund Allocator", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #111111;
        color: #f0f0f0;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #00FFF5;
        margin-top: 1rem;
        animation: fadeIn 0.7s ease-in;
    }

    .sub-info {
        font-size: 1.1rem;
        text-align: center;
        color: #AAAAAA;
        margin-bottom: 2rem;
    }

    .section {
        background-color: #1a1a1a;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.05);
    }

    .stDownloadButton button {
        background-color: #00adb5;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        transition: 0.3s ease;
    }

    .stDownloadButton button:hover {
        background-color: #00d8db;
        transform: scale(1.03);
    }

    .badge-success {
        color: #4CAF50;
        font-weight: bold;
    }

    .badge-error {
        color: #F44336;
        font-weight: bold;
    }

    .footer {
        text-align: center;
        font-size: 0.85rem;
        color: #777;
        margin-top: 2rem;
    }

    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="main-title">🧾 Mutual Fund Allocation Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-info">Upload your mutual fund `.xlsx` files to extract and summarize category allocations.</div>', unsafe_allow_html=True)

# --- Upload Section ---
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📤 Upload Excel Files")
    uploaded_files = st.file_uploader(
        "Drag and drop or browse to upload files",
        type=["xlsx"],
        accept_multiple_files=True,
        key="upload",
        help="Only Excel (.xlsx) files are supported"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- Processing Section ---
if uploaded_files:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚙️ Processing Results")

    file_dict = {file.name: file.read() for file in uploaded_files}
    valid_results = {}
    error_results = {}

    progress = st.progress(0)
    for i, (file_name, file_bytes) in enumerate(file_dict.items(), 1):
        try:
            processor = get_processor(file_name)
            df = processor(file_bytes)
            if isinstance(df, pd.DataFrame):
                valid_results[file_name] = df
            else:
                error_results[file_name] = "Processor did not return a DataFrame."
        except Exception as e:
            error_results[file_name] = str(e)
        progress.progress(i / len(file_dict))

    progress.empty()

    # --- Errors ---
    if error_results:
        st.error("❌ Some files encountered errors:")
        for fname, msg in error_results.items():
            st.markdown(f"- **{fname}**: `{msg}`")

    # --- Valid Summaries ---
    if valid_results:
        st.success(f"✅ Processed {len(valid_results)} file(s) successfully.")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for fname, df in valid_results.items():
                sheet_name = fname.split(".")[0][:31]
                with st.expander(f"📄 {sheet_name} Summary"):
                    st.dataframe(df, use_container_width=True)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)
        st.download_button(
            label="📥 Download Combined Excel",
            data=output,
            file_name="MutualFund_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="footer">Built by Dheer Doshi · © 2025 · All Rights Reserved</div>', unsafe_allow_html=True)
