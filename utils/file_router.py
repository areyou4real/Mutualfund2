from processors import (
    adityabirla, axis, baroda, hdfc, hsbc,
    icici, mahindra, mirae, shriram, sundaram
)

def get_processor(file_name: str):
    name = file_name.lower()
    if "birla" in name:
        return adityabirla.process_adityabirla
    elif "axis" in name:
        return axis.process_axis
    elif "baroda" in name:
        return baroda.process_baroda
    elif "hdfc" in name:
        return hdfc.process_hdfc
    elif "hsbc" in name:
        return hsbc.process_hsbc
    elif "icici" in name:
        return icici.process_icici
    elif "mahindra" in name:
        return mahindra.process_mahindra
    elif "mirae" in name:
        return mirae.process_mirae
    elif "shriram" in name:
        return shriram.process_shriram
    elif "sundaram" in name:
        return sundaram.process_sundaram
    else:
        raise ValueError("Unknown fund in file name: " + file_name)
