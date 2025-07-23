import pandas as pd
from io import BytesIO

def process_shriram(file_bytes):
    xls = pd.ExcelFile(BytesIO(file_bytes))
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    df_filtered = df.iloc[:, [1, 6]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    def is_valid_number(val):
        if isinstance(val, (int, float)): return True
        if isinstance(val, str):
            val = val.strip().lower()
            if val in ["", "nil", "na", "n.a.", "-", "--"]:
                return False
            try: float(val); return True
            except: return False
        return False

    def find_exact_total_after(keyword):
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword.lower() in val.lower():
                for j in range(i + 1, len(df_filtered)):
                    cat = str(df_filtered.loc[j, "Category"]).strip().lower()
                    value = df_filtered.loc[j, "Value"]
                    if cat == "total" and is_valid_number(value):
                        return float(value)
        return 0.0

    def find_sub_total_after(keyword):
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword.lower() in val.lower():
                for j in range(i + 1, len(df_filtered)):
                    cat = str(df_filtered.loc[j, "Category"]).strip().lower()
                    value = df_filtered.loc[j, "Value"]
                    if cat == "sub total" and is_valid_number(value):
                        return float(value)
        return 0.0

    net_equity_value = find_exact_total_after("Equity & Equity related")
    debt_instr = find_exact_total_after("Debt instruments")
    real_estate_sub = find_sub_total_after("Real Estate Investment Trust")
    debt_value = debt_instr + real_estate_sub

    reits_value = find_exact_total_after("reits")
    invits_value = find_exact_total_after("invits")
    treps_value = find_sub_total_after("treps")

    gold_value = silver_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            raw_val = df_filtered.loc[i, "Value"]
            if pd.notna(raw_val) and is_valid_number(raw_val):
                if "gold" in val.lower():
                    gold_value += float(raw_val)
                elif "silver" in val.lower():
                    silver_value += float(raw_val)

    net_recv_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "net receivables" in val.lower():
            if is_valid_number(df_filtered.loc[i, "Value"]):
                net_recv_value = float(df_filtered.loc[i, "Value"])
            break

    cash_value = treps_value + net_recv_value

    foreign_value = deriv_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            if val.lower().startswith("foreign"):
                for j in range(i + 1, len(df_filtered)):
                    if str(df_filtered.loc[j, "Category"]).strip().lower() == "total" and is_valid_number(df_filtered.loc[j, "Value"]):
                        foreign_value = float(df_filtered.loc[j, "Value"])
                        break
            if val.lower().startswith("derivatives"):
                for j in range(i + 1, len(df_filtered)):
                    if str(df_filtered.loc[j, "Category"]).strip().lower() == "total" and is_valid_number(df_filtered.loc[j, "Value"]):
                        deriv_value = float(df_filtered.loc[j, "Value"])
                        break

    net_equity_value -= abs(deriv_value)
    deriv_value = abs(deriv_value)

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

