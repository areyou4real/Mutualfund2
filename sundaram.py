import pandas as pd
from io import BytesIO

def process_sundaram(file_bytes):
    xls = pd.ExcelFile(BytesIO(file_bytes))
    sheet_name = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

    df_filtered = df.iloc[:, [2, 6]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    def is_valid_number(val):
        if isinstance(val, (int, float)): return True
        if isinstance(val, str):
            val = val.strip().lower()
            if val in ["", "nil", "na", "n.a.", "-", "--"]: return False
            try: float(val); return True
            except: return False
        return False

    def find_next_summary_after(keyword, target="total"):
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword.lower() in val.lower():
                for j in range(i + 1, len(df_filtered)):
                    cat = str(df_filtered.loc[j, "Category"]).strip().lower()
                    value = df_filtered.loc[j, "Value"]
                    if cat == target and is_valid_number(value):
                        return float(value)
        return 0.0

    equity_value = find_next_summary_after("Equity & Equity related", target="sub total")

    # Debt = Total for Debt Instruments + Treasury Bills
    debt_main = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "Total for Debt Instruments" in val:
            if is_valid_number(df_filtered.loc[i, "Value"]):
                debt_main = float(df_filtered.loc[i, "Value"])
            break
    treasury_value = find_next_summary_after("Treasury Bills", target="sub total")
    debt_value = debt_main + treasury_value

    reits_value = find_next_summary_after("reits")
    invits_value = find_next_summary_after("invits")
    treps_value = find_next_summary_after("Treps", target="sub total")

    # Gold and Silver
    gold_value = silver_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            v = df_filtered.loc[i, "Value"]
            if "gold" in val.lower() and is_valid_number(v): gold_value += float(v)
            elif "silver" in val.lower() and is_valid_number(v): silver_value += float(v)

    # Margin Money and Cash and Other
    margin_val = cashother_val = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            if "margin money" in val.lower() and is_valid_number(df_filtered.loc[i, "Value"]):
                margin_val = abs(float(df_filtered.loc[i, "Value"]))
            if "cash and other" in val.lower() and is_valid_number(df_filtered.loc[i, "Value"]):
                cashother_val = abs(float(df_filtered.loc[i, "Value"]))
    cash_value = abs(treps_value) - (margin_val + cashother_val)

    # Derivatives and Foreign
    deriv_value = find_next_summary_after("derivative", target="sub total")
    foreign_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and val.lower().startswith("foreign"):
            for j in range(i + 1, len(df_filtered)):
                if str(df_filtered.loc[j, "Category"]).strip().lower() == "total" and is_valid_number(df_filtered.loc[j, "Value"]):
                    foreign_value = float(df_filtered.loc[j, "Value"])
                    break
            break

    # Adjust equity
    adjusted_equity = equity_value - abs(deriv_value)
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
            adjusted_equity, debt_value, reits_value, invits_value,
            gold_value, silver_value, cash_value,
            foreign_value, deriv_value
        ]
    })

    final_df = pd.concat([summary_df, df_filtered], ignore_index=True)
    return final_df[["Tag", "Final Value"]]
