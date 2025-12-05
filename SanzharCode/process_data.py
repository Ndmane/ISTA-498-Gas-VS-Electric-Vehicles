# process_data.py
import pandas as pd
import numpy as np

def find_col(df, candidates):
    cols = df.columns
    for c in candidates:
        if c in cols:
            return c
    for c in cols:
        for pat in candidates:
            if pat in c:
                return c
    return None

def categorize_vehicle_type(series):
    if series is None:
        return pd.Series(["unknown"] * len(series))
    s = series.astype(str).str.lower()
    ev_like = s.str.contains("ev|electric|bev|phev|plug_in", regex=True)
    return np.where(ev_like, "EV_like", "ICE_like")
