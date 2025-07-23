import pandas as pd
from io import BytesIO
from processors.hdfc import process_hdfc
from processors.hsbc import process_hsbc
from processors.icici import process_icici
from processors.mahindra import process_mahindra
from processors.mirae import process_mirae
from processors.shriram import process_shriram
from processors.sundaram import process_sundaram
from processors.tata import process_tata
from processors.uti import process_uti
from processors.adityabirla import process_adityabirla

def route_fund_processor(file_name, file_bytes):
    lower_name = file_name.lower()
    if "hdfc" in lower_name:
        return process_hdfc(file_bytes)
    elif "hsbc" in lower_name:
        return process_hsbc(file_bytes)
    elif "icici" in lower_name:
        return process_icici(file_bytes)
    elif "mahindra" in lower_name:
        return process_mahindra(file_bytes)
    elif "mirae" in lower_name:
        return process_mirae(file_bytes)
    elif "shriram" in lower_name:
        return process_shriram(file_bytes)
    elif "sundaram" in lower_name:
        return process_sundaram(file_bytes)
    elif "tata" in lower_name:
        return process_tata(file_bytes)
    elif "uti" in lower_name:
        return process_uti(file_bytes)
    elif "aditya" in lower_name or "birla" in lower_name:
        return process_adityabirla(file_bytes)
    else:
        return f"Unknown fund name: {file_name}"
