# utils/file_router.py

import os

from processors import (
    adityabirla,
    axis,
    baroda,
    hdfc,
    hsbc,
    icici,
    mahindra,
    mirae,
    shriram,
    sundaram,
)

FUND_MAPPING = {
    "adityabirla": adityabirla.process_adityabirla,
    "axis": axis.process_axis,
    "baroda": baroda.process_baroda,
    "hdfc": hdfc.process_hdfc,
    "hsbc": hsbc.process_hsbc,
    "icici": icici.process_icici,
    "mahindra": mahindra.process_mahindra,
    "mirae": mirae.process_mirae,
    "shriram": shriram.process_shriram,
    "sundaram": sundaram.process_sundaram,
}

def route_file(filename: str):
    """
    Returns the processing function based on the fund name in filename.
    """
    base_name = os.path.basename(filename).lower()
    for key in FUND_MAPPING:
        if key in base_name:
            return FUND_MAPPING[key]
    return None
