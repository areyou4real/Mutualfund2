import pandas as pd
from io import BytesIO

def process_adityabirla(file_bytes):
    xls = pd.ExcelFile(BytesIO(file_bytes))
    sheet = xls.sheet_names[0]
    df = xls.parse(sheet)

    if df.shape[1] < 7:
        raise Exception("Not enough columns to extract 2nd and 7th.")

    df = df.iloc[:, [1, 6]]
    df.columns = df.columns.str.strip()
    df = df.dropna(how='all').reset_index(drop=True)

    while df.shape[1] < 4:
        df[f"extra_{df.shape[1] + 1}"] = None

    insert_values_col4 = []
    insert_labels_col3 = []

    # Derivatives
    section_sum = 0
    count = 0
    for idx in range(len(df)):
        val = str(df.iloc[idx, 0]).lower()
        if "disclosure in derivatives" in val:
            j = idx
            while j < len(df):
                cell_val = df.iloc[j, 1]
                if pd.isna(cell_val) and count > 0:
                    break
                elif pd.notna(cell_val):
                    try:
                        section_sum += float(cell_val)
                        count += 1
                    except:
                        pass
                j += 1
            break
    if count > 0:
        insert_labels_col3.append("Hedged Equity")
        insert_values_col4.append(section_sum)

    # Gold & Silver
    for metal, tag in [("gold", "Gold"), ("silver", "Silver")]:
        for idx, row in df.iterrows():
            desc = str(row.iloc[0]).lower()
            if metal in desc:
                try:
                    val = float(row.iloc[1])
                    insert_labels_col3.append(tag)
                    insert_values_col4.append(val)
                except:
                    pass
                break

    # Section-based tag assignment
    def section_total(start_phrase, label, stop_on_total=True):
        total = count = 0
        for idx, row in df.iterrows():
            if start_phrase.lower() in str(row.iloc[0]).lower():
                j = idx
                while j < len(df):
                    val = str(df.iloc[j, 0]).lower()
                    if any(x in val for x in ["total", "sub total", "grand total"]) and stop_on_total:
                        break
                    cell_val = df.iloc[j, 1]
                    if pd.isna(cell_val) and count > 0:
                        break
                    elif pd.notna(cell_val):
                        try:
                            total += float(cell_val)
                            count += 1
                        except:
                            pass
                    j += 1
                break
        if count > 0:
            insert_labels_col3.append(label)
            insert_values_col4.append(total)

    section_total("reit", "ReIT")
    section_total("invit", "InvIT")
    section_total("foreign securities", "International Equity")

    # Equity & Debt Totals
    equity_val = None
    def total_after_section(section_name, label):
        nonlocal equity_val
        for idx, row in df.iterrows():
            if str(row.iloc[0]).strip().lower() == section_name.lower():
                for j in range(idx + 1, len(df)):
                    val = str(df.iloc[j, 0]).strip().lower()
                    if val == "total":
                        try:
                            v = float(df.iloc[j, 1])
                            if label == "Net Equity":
                                equity_val = v
                            insert_labels_col3.append(label)
                            insert_values_col4.append(v)
                        except:
                            pass
                        return

    total_after_section("Equity & Equity related", "Net Equity")
    total_after_section("Debt Instruments", "Debt")

    # Cash & Others
    def cash_sum(term):
        total = count = 0
        for idx, row in df.iterrows():
            if term.lower() in str(row.iloc[0]).lower():
                j = idx
                while j < len(df):
                    val = str(df.iloc[j, 0]).lower()
                    if "total" in val:
                        break
                    cell_val = df.iloc[j, 1]
                    if pd.isna(cell_val) and count > 0:
                        break
                    elif pd.notna(cell_val):
                        try:
                            total += float(cell_val)
                            count += 1
                        except:
                            pass
                    j += 1
                break
        return total if count > 0 else 0

    treps = cash_sum("TREPS")
    netrec = cash_sum("Net Receivables")
    margin_val = 0
    for idx in range(len(df)):
        if "margin" in str(df.iloc[idx, 0]).lower():
            try:
                margin_val = float(df.iloc[idx, 1])
            except:
                pass
            break
    cash_total = treps + netrec + margin_val
    if cash_total != 0:
        insert_labels_col3.append("Cash & Others")
        insert_values_col4.append(cash_total)

    # Market Instruments under Debt
    market_total = 0
    for idx, row in df.iterrows():
        if "market instruments" in str(row.iloc[0]).lower():
            j = idx
            while j < len(df):
                val = str(df.iloc[j, 0]).lower()
                if "total" in val:
                    break
                cell_val = df.iloc[j, 1]
                if pd.notna(cell_val):
                    try:
                        market_total += float(cell_val)
                    except:
                        pass
                j += 1
            break
    for i, lbl in enumerate(insert_labels_col3):
        if lbl == "Debt":
            insert_values_col4[i] += market_total

    # Hedged Equity offset
    for i, lbl in enumerate(insert_labels_col3):
        if lbl == "Net Equity":
            for j, lbl2 in enumerate(insert_labels_col3):
                if lbl2 == "Hedged Equity":
                    insert_values_col4[i] -= abs(insert_values_col4[j])
                    insert_values_col4[j] = abs(insert_values_col4[j])
                    break
            break

    return pd.DataFrame({
        "Tag": insert_labels_col3,
        "Final Value": insert_values_col4
    })
