import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor

st.set_page_config(page_title="Mutual Fund Allocation Generator", layout="centered")
st.title("🧾 Mutual Fund Allocation Generator")
st.markdown("Upload one or more mutual fund Excel files. The app will detect the allocations and return a cleaned summary.")

uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    file_dict = {file.name: file.read() for file in uploaded_files}
    results = {}

    with st.spinner("Processing files..."):
        for name, data in file_dict.items():
            try:
                processor = get_processor(name)
                if processor:
                    df = processor(data)
                    # Convert to float if possible, format safely
                    df["Final Value"] = df["Final Value"].apply(lambda x: f"{float(x):.2f}" if isinstance(x, (int, float, float)) or str(x).replace('.', '', 1).isdigit() else x)
                    results[name] = df
                else:
                    results[name] = f"No processor found for file: {name}"
            except Exception as e:
                results[name] = f"Error processing {name}: {str(e)}"

    valid_results = {k: v for k, v in results.items() if isinstance(v, pd.DataFrame)}
    error_results = {k: v for k, v in results.items() if not isinstance(v, pd.DataFrame)}

    if error_results:
        st.subheader("❌ Errors")
        for name, error in error_results.items():
            st.error(f"{name}: {error}")

    if valid_results:
        st.subheader("✅ Fund Summaries")
        for name, df in valid_results.items():
            with st.expander(f"{name.title()} Summary"):
                st.dataframe(df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for name, df in valid_results.items():
                sheet_name = name.replace(".xlsx", "")[:31]  # Sheet name max length
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)

        st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{0}" download="Allocation_Output.xlsx">
                    <button style='padding: 0.5em 1em; font-size: 1em;'>📥 Download All Results</button>
                </a>
            </div>
        """.format(output.getvalue().hex()), unsafe_allow_html=True)
    else:
        st.warning("No valid dataframes to display or download.")
