import pandas as pd
from io import BytesIO

def process_hdfc(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), sheet_name="MY2005", header=None)
    df_filtered = df.iloc[:, [1, 3, 7, 10, 11]]
    df_filtered.columns = ["ISIN/Description", "Name", "Exposure", "Value 1", "Value 2"]
    df_filtered["Tag"] = None
    df_filtered["Value"] = None
    insert_row = 0

    portfolio_start = None
    for idx, val in enumerate(df_filtered.iloc[:, 0]):
        if isinstance(val, str) and "portfolio classification" in val.lower():
            portfolio_start = idx
            break

    if portfolio_start is not None:
        for j in range(portfolio_start + 1, len(df_filtered)):
            if "equity" in str(df_filtered.iloc[j, 0]).lower():
                df_filtered.at[insert_row, "Value"] = df_filtered.iloc[j, 1]
                df_filtered.at[insert_row, "Tag"] = "Net Equity"
                insert_row += 1
                break

        for j in range(portfolio_start + 1, len(df_filtered)):
            if "total hedged exposure" in str(df_filtered.iloc[j, 0]).lower():
                df_filtered.at[insert_row, "Value"] = df_filtered.iloc[j, 1]
                df_filtered.at[insert_row, "Tag"] = "Hedged Equity"
                insert_row += 1
                break

    reit_val = invit_val = 0.0
    for j in range(portfolio_start + 1, len(df_filtered)):
        val = str(df_filtered.iloc[j, 0]).lower()
        if "units issued by reit" in val:
            try: reit_val = float(df_filtered.iloc[j, 1])
            except: pass
        if "units issued by invit" in val:
            try: invit_val = float(df_filtered.iloc[j, 1])
            except: pass
    df_filtered.at[insert_row, "Value"] = reit_val + invit_val
    df_filtered.at[insert_row, "Tag"] = "ReIT/InvIT"
    insert_row += 1

    for j in range(portfolio_start + 1, len(df_filtered)):
        if "cash" in str(df_filtered.iloc[j, 0]).lower():
            df_filtered.at[insert_row, "Value"] = df_filtered.iloc[j, 1]
            df_filtered.at[insert_row, "Tag"] = "Cash & Others"
            insert_row += 1
            break

    gold_value = 0.0
    for idx in range(len(df_filtered)):
        name_val = df_filtered.iloc[idx, 1]
        if isinstance(name_val, str) and "gold" in name_val.lower() and "fund" in name_val.lower():
            try: gold_value += float(df_filtered.iloc[idx, 2])
            except: continue
    if gold_value > 0:
        df_filtered.loc[insert_row, "Value"] = gold_value
        df_filtered.loc[insert_row, "Tag"] = "Gold"
        insert_row += 1

    silver_total = 0.0
    for idx in range(len(df_filtered)):
        name_val = df_filtered.iloc[idx, 1]
        if isinstance(name_val, str) and "silver" in name_val.lower():
            for j in range(idx, len(df_filtered)):
                val = df_filtered.iloc[j, 2]
                if pd.isna(val) and j != idx: break
                try: silver_total += float(val)
                except: pass
            break
    df_filtered.at[insert_row, "Value"] = silver_total
    df_filtered.at[insert_row, "Tag"] = "Silver"
    insert_row += 1

    debt_val = cd_value = 0.0
    for idx, val in enumerate(df_filtered.iloc[:, 0]):
        if isinstance(val, str) and val.strip().lower() == "debt instruments":
            for j in range(idx + 1, len(df_filtered)):
                if str(df_filtered.iloc[j, 0]).strip().lower() == "total":
                    try: debt_val = float(df_filtered.iloc[j, 2])
                    except: pass
                    break
            break
    for j in range(portfolio_start + 1, len(df_filtered)):
        if "cd" in str(df_filtered.iloc[j, 0]).lower():
            try: cd_value = float(df_filtered.iloc[j, 1])
            except: pass
            break
    df_filtered.at[insert_row, "Value"] = debt_val + cd_value
    df_filtered.at[insert_row, "Tag"] = "Debt"
    insert_row += 1

    intl_value = 0.0
    for idx, val in enumerate(df_filtered.iloc[:, 0]):
        if isinstance(val, str) and val.strip().lower() == "international":
            for j in range(idx + 1, len(df_filtered)):
                if str(df_filtered.iloc[j, 0]).strip().lower() == "total":
                    try: intl_value = float(df_filtered.iloc[j, 2])
                    except: pass
                    break
            break
    df_filtered.at[insert_row, "Value"] = intl_value
    df_filtered.at[insert_row, "Tag"] = "International equity"
    insert_row += 1

    df_filtered = df_filtered.rename(columns={"Value": "Final Value"})
    return df_filtered[["Tag", "Final Value"]].dropna()

