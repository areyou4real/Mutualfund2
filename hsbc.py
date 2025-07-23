import pandas as pd
from io import BytesIO

def process_hsbc(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), header=None)
    df_filtered = df.iloc[:, [0, 5]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    def find_total_after(keyword, n=1):
        count = 0
        total = 0.0
        start = None
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword.lower() in val.lower():
                start = i
                break
        if start is not None:
            for j in range(start + 1, len(df_filtered)):
                val = str(df_filtered.loc[j, "Category"]).strip().lower()
                if val == "total" or val == "sub total":
                    try:
                        val_to_add = float(df_filtered.loc[j, "Value"])
                        if not pd.isna(val_to_add):
                            total += val_to_add
                            count += 1
                    except:
                        pass
                    if count == n:
                        break
        return total

    net_equity_value = find_total_after("Equity & Equity Related Instruments", 1)
    debt_value = find_total_after("Debt Instruments", 3)
    gold_value = find_total_after("Exchange Traded Fund", 1)

    # Cash (TREPS + Net Current Assets)
    treps_value = nca_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            if "treps" in val.lower():
                try:
                    treps_value = float(df_filtered.loc[i, "Value"])
                except: pass
            if "net current assets" in val.lower():
                try:
                    nca_value = float(df_filtered.loc[i, "Value"])
                except: pass
    cash_value = treps_value + nca_value

    # ReIT/InvIT
    reit_invit_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and ("reits" in val.lower() or "invits" in val.lower()):
            reit_invit_value = find_total_after(val, 1)
            break

    # International Equity
    foreign_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "foreign" in val.lower():
            foreign_value = find_total_after(val, 1)
            break

    # Silver
    silver_value = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "silver" in val.lower():
            try:
                silver_value += float(df_filtered.loc[i, "Value"])
            except:
                pass

    summary_df = pd.DataFrame({
        "Category": [None] * 7,
        "Value": [None] * 7,
        "Tag": [
            "Net Equity", "Debt", "Gold", "Cash",
            "ReIT/InvIT", "International Equity", "Silver"
        ],
        "Final Value": [
            net_equity_value, debt_value, gold_value, cash_value,
            reit_invit_value, foreign_value, silver_value
        ]
    })

    final_df = pd.concat([summary_df, df_filtered], ignore_index=True)
    return final_df[["Tag", "Final Value"]]
