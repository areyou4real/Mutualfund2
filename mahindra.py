import pandas as pd
from io import BytesIO

def process_mahindra(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), sheet_name="MMF23", header=None)
    df_filtered = df.iloc[:, [1, 6]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    def find_exact_total_after(keyword, first_word_only=False, allow_sub_total=False):
        start = None
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str):
                val_lower = val.lower().strip()
                if first_word_only:
                    if val_lower.startswith(keyword.lower()):
                        start = i
                        break
                elif keyword.lower() in val_lower:
                    start = i
                    break
        if start is not None:
            for j in range(start + 1, len(df_filtered)):
                val = str(df_filtered.loc[j, "Category"]).strip().lower()
                if val == "total" or (allow_sub_total and "total" in val):
                    try:
                        return float(df_filtered.loc[j, "Value"])
                    except:
                        return 0.0
        return 0.0

    # Major components
    net_equity_value = find_exact_total_after("Equity & Equity related")
    debt_value = find_exact_total_after("Debt instruments")
    reits_value = find_exact_total_after("reits")
    invits_value = find_exact_total_after("invits")
    treps_value = find_exact_total_after("treps")

    # Gold and Silver
    gold_value = silver_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            if "gold" in val.lower():
                try:
                    v = float(df_filtered.loc[i, "Value"])
                    if not pd.isna(v): gold_value += v
                except: pass
            if "silver" in val.lower():
                try:
                    v = float(df_filtered.loc[i, "Value"])
                    if not pd.isna(v): silver_value += v
                except: pass

    # Net Receivables
    net_recv_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "net receivables" in val.lower():
            try:
                net_recv_value = float(df_filtered.loc[i, "Value"])
            except:
                pass
            break
    cash_value = treps_value + net_recv_value

    # Foreign = International Equity
    foreign_value = find_exact_total_after("foreign", first_word_only=True)

    # Derivatives = Hedged Equity
    deriv_value = find_exact_total_after("derivatives", first_word_only=True)

    summary_df = pd.DataFrame({
        "Category": [None] * 9,
        "Value": [None] * 9,
        "Tag": [
            "Equity", "Debt", "ReITs", "InvITs",
            "Gold", "Silver", "Cash",
            "International Equity", "Hedged Equity"
        ],
        "Final Value": [
            net_equity_value, debt_value, reits_value, invits_value,
            gold_value, silver_value, cash_value,
            foreign_value, deriv_value
        ]
    })

    final_df = pd.concat([summary_df, df_filtered], ignore_index=True)
    return final_df[["Tag", "Final Value"]]
