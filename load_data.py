# load_data.py
import pandas as pd

def smart_read_csv(path):
    for encoding in ["utf-8", "utf-8-sig", "ISO-8859-1"]:
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False)
        except:
            continue
    return pd.read_csv(path, low_memory=False)

def load_data(cars_path, ev_path):
    cars = smart_read_csv(cars_path)
    ev = smart_read_csv(ev_path)
    return cars, ev