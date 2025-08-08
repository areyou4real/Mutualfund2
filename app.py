import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_router import get_processor
import traceback

# =============================
# Page / App Config
# =============================
st.set_page_config(
    page_title="🧾 Mutual Fund Allocator",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session State ----------
if "uploaded_bytes" not in st.session_state:
    st.session_state.uploaded_bytes = {}
if "results" not in st.session_state:
    st.session_state.results = {"valid": {}, "error": {}}
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# =============================
# Theming (Light / Dark)
# =============================
with st.sidebar:
    st.markdown("## 🎛️ Controls")
    theme_choice = st.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme=="Dark" else 1)
    st.session_state.theme = theme_choice
    st.markdown("---")

# CSS variables based on theme
IS_DARK = st.session_state.theme == "Dark"
BG = "#0f1115" if IS_DARK else "#f7f9fc"
CARD = "#1a1f2b" if IS_DARK else "#ffffff"
TEXT = "#e6eaf2" if IS_DARK else "#0f172a"
SUB = "#93c5fd" if IS_DARK else "#334155"
ACCENT = "#22d3ee" if IS_DARK else "#0ea5e9"
ACCENT2 = "#a78bfa" if IS_DARK else "#7c3aed"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
WARN = "#f59e0b"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
        background: linear-gradient(155deg, {BG} 0%, {BG} 60%, rgba(34,211,238,0.06) 100%);
        color: {TEXT};
    }}

    /* Title */
    .main-title {{
        font-size: 3rem; font-weight: 800; text-align: center; margin: 0.3rem 0 0.5rem 0;
        color: {ACCENT}; letter-spacing: 0.5px;
        animation: fadeIn 0.7s ease-in;
    }}
    .sub-info {{
        font-size: 1.05rem; text-align: center; color: {SUB}; margin-bottom: 1.2rem;
    }}

    /* Cards */
    .section {{
        background: {CARD}; border: 1px solid rgba(148,163,184,0.2); border-radius: 16px;
        padding: 1.2rem 1.2rem; margin-bottom: 1rem; box-shadow: 0 8px 30px rgba(2,12,27,0.25);
    }}

    /* Buttons */
    .stDownloadButton button {{
        background: {ACCENT}; color: white; font-weight: 700; border-radius: 12px; padding: 0.7rem 1.2rem;
        border: none; transition: transform .1s ease, box-shadow .2s ease; box-shadow: 0 6px 18px rgba(34,211,238,.25);
    }}
    .stDownloadButton button:hover {{ transform: translateY(-1px); box-shadow: 0 10px 24px rgba(34,211,238,.35); }}

    /* Badges */
    .badge {{ display:inline-block; padding: 0.18rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }}
    .badge-success {{ background: rgba(34,197,94,.15); color: {SUCCESS}; }}
    .badge-error {{ background: rgba(239,68,68,.15); color: {ERROR}; }}
    .badge-warn {{ background: rgba(245,158,11,.15); color: {WARN}; }}

    /* Expander */
    details summary {{ cursor: pointer; }}

    /* Metric pill */
    .pill {{
        display:inline-flex; align-items:center; gap: .5rem; border: 1px dashed rgba(148,163,184,0.4);
        padding: .35rem .7rem; border-radius: 12px; font-size: .9rem; color: {SUB}; margin-right: .5rem;
    }}

    /* Footer */
    .footer {{ text-align:center; font-size: .85rem; color: {SUB}; margin-top: 1rem; }}

    @keyframes fadeIn {{ from {{opacity: 0; transform: translateY(4px)}} to {{opacity: 1; transform: translateY(0)}} }}
    </style>
""", unsafe_allow_html=True)

# =============================
# Header
# =============================
st.markdown('<div class="main-title">🧾 Mutual Fund Allocation Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-info">Upload your mutual fund <code>.xlsx</code> files to extract and summarize category allocations. Elegant UI, robust errors, clean downloads.</div>', unsafe_allow_html=True)

# =============================
# Sidebar: Tips / Actions
# =============================
with st.sidebar:
    st.markdown("### 📌 Tips")
    st.markdown(
        "- File names decide sheet names (trimmed to 31 chars).\n"
        "- Each processor must return a Pandas DataFrame.\n"
        "- Use the per-file expander to preview results.\n"
        "- Download button saves **one** Excel with all sheets.")

    st.markdown("### 🧹 Session")
    if st.button("Reset All", type="secondary"):
        st.session_state.uploaded_bytes = {}
        st.session_state.results = {"valid": {}, "error": {}}
        st.toast("Session cleared.")
        st.experimental_rerun()

# =============================
# Upload Section
# =============================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("📤 Upload Excel Files")
uploaded_files = st.file_uploader(
    "Drag & drop or browse to upload (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True,
    key="upload",
    help="Only Excel (.xlsx) files are supported"
)

# Persist file bytes across reruns so preview/actions don't lose data
if uploaded_files:
    for f in uploaded_files:
        try:
            # Streamlit uploads are file-like; read once and store
            st.session_state.uploaded_bytes[f.name] = f.read()
        except Exception:
            # Some browsers forbid multiple reads; ignore
            pass
st.markdown('</div>', unsafe_allow_html=True)

# =============================
# Processing Section
# =============================
if st.session_state.uploaded_bytes:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("⚙️ Processing Results")

    files_map = dict(st.session_state.uploaded_bytes)  # shallow copy

    valid_results: dict[str, pd.DataFrame] = {}
    error_results: dict[str, str] = {}

    # Progress and live log
    progress = st.progress(0)
    log = st.empty()

    for i, (file_name, file_bytes) in enumerate(files_map.items(), start=1):
        try:
            log.info(f"Processing **{file_name}** …")
            processor = get_processor(file_name)
            df = processor(file_bytes)
            if not isinstance(df, pd.DataFrame):
                raise TypeError("Processor did not return a pandas DataFrame")

            # Light sanity: limit columns to <= 50 to avoid huge sheets
            if df.shape[1] > 200:
                raise ValueError("Unusually wide DataFrame (>200 columns). Check your processor output.")

            valid_results[file_name] = df
        except Exception as e:
            tb = "\n".join(traceback.format_exception_only(type(e), e)).strip()
            error_results[file_name] = tb
        finally:
            progress.progress(i / max(len(files_map), 1))

    progress.empty(); log.empty()

    # Message blocks
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: st.markdown(f"<span class='pill'>📄 Files: <b>{len(files_map)}</b></span>", unsafe_allow_html=True)
    with c2: st.markdown(f"<span class='pill'>✅ Success: <b>{len(valid_results)}</b></span>", unsafe_allow_html=True)
    with c3: st.markdown(f"<span class='pill'>❌ Errors: <b>{len(error_results)}</b></span>", unsafe_allow_html=True)

    # Error panel (if any)
    if error_results:
        st.error("Some files failed to process.")
        with st.expander("See error details", expanded=False):
            for fname, msg in error_results.items():
                st.markdown(f"**{fname}**  ")
                st.code(msg, language="text")

    # Valid summaries
    if valid_results:
        st.success(f"Processed {len(valid_results)} file(s) successfully.")

        # Overview table
        overview_rows = []
        for fname, df in valid_results.items():
            overview_rows.append({
                "File": fname,
                "Rows": df.shape[0],
                "Columns": df.shape[1],
                "Column names": ", ".join(map(str, list(df.columns)[:6])) + (" …" if df.shape[1] > 6 else "")
            })
        overview = pd.DataFrame(overview_rows)
        with st.expander("📊 Quick Overview (all processed files)", expanded=False):
            st.dataframe(overview, use_container_width=True, hide_index=True)

        # Per-file tabs/expanders
        for fname, df in valid_results.items():
            sheet_name = fname.split(".")[0][:31]
            with st.expander(f"📄 {sheet_name} — preview & actions", expanded=False):
                t1, t2, t3 = st.tabs(["Preview", "Info", "Export one sheet"])
                with t1:
                    st.dataframe(df, use_container_width=True)
                with t2:
                    cA, cB, cC = st.columns([1,1,1])
                    with cA: st.metric("Rows", df.shape[0])
                    with cB: st.metric("Columns", df.shape[1])
                    with cC: st.metric("Memory (KB)", f"{df.memory_usage(index=True).sum() / 1024:.1f}")
                    st.markdown("**Columns:**")
                    st.code("\n".join(map(str, df.columns.tolist())), language="text")
                with t3:
                    buf_one = BytesIO()
                    # Always write a new workbook with a single sheet of this df
                    with pd.ExcelWriter(buf_one, engine='openpyxl') as w:
                        df.to_excel(w, sheet_name=sheet_name, index=False)
                    one_bytes = buf_one.getvalue()
                    st.download_button(
                        label=f"⬇️ Download '{sheet_name}.xlsx'",
                        data=one_bytes,
                        file_name=f"{sheet_name}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

        # Combined Excel for all
        out_all = BytesIO()
        with pd.ExcelWriter(out_all, engine='openpyxl') as writer:
            for fname, df in valid_results.items():
                safe_sheet = fname.split(".")[0][:31] or "Sheet"
                df.to_excel(writer, sheet_name=safe_sheet, index=False)
        all_bytes = out_all.getvalue()  # safer than seek+read

        st.download_button(
            label="📥 Download Combined Excel",
            data=all_bytes,
            file_name="MutualFund_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# Footer
# =============================
st.markdown(
    f"<div class='footer'>Built by Dheer Doshi · © 2025 · All Rights Reserved · Theme: <b>{st.session_state.theme}</b></div>",
    unsafe_allow_html=True,
)
