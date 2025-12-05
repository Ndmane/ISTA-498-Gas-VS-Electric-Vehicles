# clean_data.py
import pandas as pd

def normalize_columns(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df

def clean_data(cars, ev):
    cars = normalize_columns(cars).drop_duplicates()
    ev = normalize_columns(ev).drop_duplicates()
    return cars, ev