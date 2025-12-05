# combined_pipeline.py
# === load_data.py ===
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


# === clean_data.py ===
def normalize_columns(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    return df

def clean_data(cars, ev):
    cars = normalize_columns(cars).drop_duplicates()
    ev = normalize_columns(ev).drop_duplicates()
    return cars, ev


# === process_data.py ===
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


# === create_visuals.py ===
import matplotlib.pyplot as plt
from pathlib import Path

def save_plot(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


# === main ===
def main():
    cars_path = "Data/Cars_Datasets_2025.csv"
    ev_path   = "Data/Electric_Vehicle_Population_Data.csv"

    out = Path("sanjar_outputs/combined")
    out.mkdir(parents=True, exist_ok=True)

    cars, ev = load_data(cars_path, ev_path)
    cars, ev = clean_data(cars, ev)

    print("Combined pipeline complete")


if __name__ == "__main__":
    main()
