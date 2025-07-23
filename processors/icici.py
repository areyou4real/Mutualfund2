import pandas as pd
from io import BytesIO

def process_icici(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), sheet_name='MULTI', header=None)
    df_filtered = df.iloc[:, [1, 7]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    final_values = {
        "Debt": 0.0,
        "International Equity": 0.0,
        "ReIT/InvIT": 0.0,
        "Gold": 0.0,
        "Silver": 0.0,
        "Commodity Derivatives": 0.0,
        "Hedged equity": 0.0,
        "Net equity": 0.0,
        "Cash & others": 0.0
    }

    debt_keywords = [
        "Debt Instruments", "Money Market Instruments",
        "Compulsory Convertible Debenture"
    ]
    for keyword in debt_keywords:
        for idx, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword.lower() in val.lower():
                try:
                    final_values["Debt"] += float(df_filtered.loc[idx, "Value"])
                    break
                except:
                    pass

    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "foreign securities" in val.lower():
            try:
                final_values["International Equity"] += float(df_filtered.loc[idx, "Value"])
            except:
                pass
            break

    reit_invit_keywords = ["reit", "invit"]
    found = set()
    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            lower_val = val.lower()
            for keyword in reit_invit_keywords:
                if keyword in lower_val and keyword not in found:
                    try:
                        final_values["ReIT/InvIT"] += float(df_filtered.loc[idx, "Value"])
                        found.add(keyword)
                    except:
                        pass
            if len(found) == len(reit_invit_keywords):
                break

    etf_keywords = {"Gold": "gold etf", "Silver": "silver etf"}
    for tag, keyword in etf_keywords.items():
        for idx, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword in val.lower():
                try:
                    final_values[tag] += float(df_filtered.loc[idx, "Value"])
                except:
                    pass
                break

    # Commodity Derivatives
    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "exchange traded commodity derivatives" in val.lower():
            total = 0.0
            started = False
            for j in range(idx, len(df_filtered)):
                cell_val = df_filtered.loc[j, "Value"]
                if pd.isna(cell_val):
                    if started: break
                    continue
                try:
                    total += float(cell_val)
                    started = True
                except:
                    if started: break
            final_values["Commodity Derivatives"] += total
            break

    # Hedged Equity
    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "stock / index futures" in val.lower():
            total = 0.0
            started = False
            for j in range(idx, len(df_filtered)):
                cell_val = df_filtered.loc[j, "Value"]
                if pd.isna(cell_val):
                    if started: break
                    continue
                try:
                    total += float(cell_val)
                    started = True
                except:
                    if started: break
            final_values["Hedged equity"] += total
            break

    # Net Equity
    equity_start = None
    listed_val = None
    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "equity" in val.lower():
            equity_start = idx
            break
    if equity_start is not None:
        for j in range(equity_start + 1, len(df_filtered)):
            val = df_filtered.loc[j, "Category"]
            if isinstance(val, str) and "listed" in val.lower():
                try:
                    listed_val = float(df_filtered.loc[j, "Value"])
                except:
                    pass
                break
    if listed_val is not None:
        final_values["Net equity"] = listed_val - abs(final_values["Hedged equity"])
        final_values["Hedged equity"] = abs(final_values["Hedged equity"])

    # Cash & Others
    cash_keywords = ["TREPS", "Net current assets"]
    cash_total = 0.0
    found_cash = set()
    for idx, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str):
            lower_val = val.lower()
            for keyword in cash_keywords:
                if keyword.lower() in lower_val and keyword not in found_cash:
                    try:
                        cash_total += float(df_filtered.loc[idx, "Value"])
                        found_cash.add(keyword)
                    except:
                        pass
        if len(found_cash) == len(cash_keywords):
            break
    final_values["Cash & others"] = cash_total

    summary_rows = pd.DataFrame({
        "Category": [None] * len(final_values),
        "Value": [None] * len(final_values),
        "Tag": list(final_values.keys()),
        "Final Value": list(final_values.values())
    })

    df_combined = pd.concat([summary_rows, df_filtered], ignore_index=True)
    return df_combined[["Tag", "Final Value"]]
