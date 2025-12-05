# full_pipeline.py
from load_data import load_data
from clean_data import clean_data
from process_data import find_col

import pandas as pd
from pathlib import Path

def main():
    cars_path = "Data/Cars_Datasets_2025.csv"
    ev_path   = "Data/Electric_Vehicle_Population_Data.csv"

    out_tables = Path("sanjar_outputs/full_pipeline/tables")
    out_tables.mkdir(parents=True, exist_ok=True)

    cars, ev = load_data(cars_path, ev_path)
    cars, ev = clean_data(cars, ev)

    ev_make = find_col(ev, ["make", "brand", "manufacturer"])
    if ev_make:
        ev_brand = ev[ev_make].value_counts().reset_index()
        ev_brand.columns = ["make", "count"]
        ev_brand.to_csv(out_tables / "ev_brand_distribution.csv", index=False)

    print("Basic pipeline complete")

if __name__ == "__main__":
    main()
