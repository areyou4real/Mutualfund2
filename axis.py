import pandas as pd
from io import BytesIO

def process_axis(file_bytes):
    df = pd.read_excel(BytesIO(file_bytes), header=None)
    df_filtered = df.iloc[:, [1, 6]].copy()
    df_filtered.columns = ["Category", "Value"]
    df_filtered["Tag"] = None
    df_filtered["Final Value"] = None

    tags = [
        "Hedged Equity", "Net Equity", "Debt", "Gold",
        "Silver", "International Equity", "ReIT/InvIT", "Cash & others"
    ]
    final_values = {tag: 0.0 for tag in tags}

    def get_total_after_match(start_idx, allowed_totals):
        for i in range(start_idx + 1, len(df_filtered)):
            val = str(df_filtered.loc[i, "Category"]).strip().lower()
            if any(val == at for at in allowed_totals):
                try:
                    return float(df_filtered.loc[i, "Value"])
                except:
                    return 0.0
        return 0.0

    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "derivatives" in val.lower():
            final_values["Hedged Equity"] = get_total_after_match(i, ["total"])
            break

    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "equity & equity related" in val.lower():
            final_values["Net Equity"] = get_total_after_match(i, ["total"])
            break

    debt_total = 0.0
    for keyword in ["debt instruments", "money market instruments"]:
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword in val.lower():
                debt_total += get_total_after_match(i, ["total"])
                break
    final_values["Debt"] = debt_total

    final_values["Net Equity"] -= abs(final_values["Hedged Equity"])
    final_values["Hedged Equity"] = abs(final_values["Hedged Equity"])

    def sum_keyword(keyword):
        total = 0.0
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and keyword in val.lower():
                try:
                    total += float(df_filtered.loc[i, "Value"])
                except:
                    continue
        return total

    final_values["Gold"] = sum_keyword("gold")
    final_values["Silver"] = sum_keyword("silver")

    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "foreign" in val.lower():
            final_values["International Equity"] = get_total_after_match(i, ["total"])
            break

    reit_invit_total = 0.0
    for keyword in ["reit", "invit"]:
        for i, val in enumerate(df_filtered["Category"]):
            if isinstance(val, str) and val.lower().startswith(keyword):
                reit_invit_total += get_total_after_match(i, ["total", "sub total"])
                break
    final_values["ReIT/InvIT"] = reit_invit_total

    reverse_val = 0.0
    net_recv_val = 0.0
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "reverse repo" in val.lower():
            reverse_val = get_total_after_match(i, ["sub total"])
            break
    for i, val in enumerate(df_filtered["Category"]):
        if isinstance(val, str) and "net receivables" in val.lower():
            try:
                net_recv_val = float(df_filtered.loc[i, "Value"])
            except:
                net_recv_val = 0.0
            break

    final_values["Cash & others"] = reverse_val + net_recv_val

    summary_df = pd.DataFrame({
        "Category": [None] * len(final_values),
        "Value": [None] * len(final_values),
        "Tag": list(final_values.keys()),
        "Final Value": list(final_values.values())
    })

    final_df = pd.concat([summary_df, df_filtered], ignore_index=True)
    return final_df.iloc[:, [2, 3]]  # Tag, Final Value
