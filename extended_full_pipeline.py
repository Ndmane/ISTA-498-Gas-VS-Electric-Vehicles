# extended_full_pipeline.py
"""
Full pipeline for EV vs ICE analysis.
Loads datasets, cleans, processes, generates visualizations, and saves tables.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from load_data import load_data
from clean_data import clean_data
from process_data import find_col
from create_visuals import save_plot


def main():
    cars_path = "Data/Cars_Datasets_2025.csv"
    ev_path   = "Data/Electric_Vehicle_Population_Data.csv"

    out_base  = Path("sanjar_outputs/full_pipeline")
    out_plots = out_base / "plots"
    out_tables = out_base / "tables"

    out_plots.mkdir(parents=True, exist_ok=True)
    out_tables.mkdir(parents=True, exist_ok=True)

    # Load
    cars, ev = load_data(cars_path, ev_path)

    # Clean
    cars, ev = clean_data(cars, ev)

    # DETECT KEY COLUMNS
    ev_make = find_col(ev, ["make", "brand", "manufacturer"])
    ev_model = find_col(ev, ["model"])
    ev_year = find_col(ev, ["model_year", "year"])
    ev_range = find_col(ev, ["electric_range", "range"])
    ev_state = find_col(ev, ["state", "us_state"])

    # EV brand distribution
    if ev_make:
        ev_brand = ev[ev_make].value_counts().reset_index()
        ev_brand.columns = ["make", "count"]
        ev_brand.to_csv(out_tables / "ev_brand_distribution.csv", index=False)

    # EV by year
    if ev_year:
        ev_by_year = ev[ev_year].value_counts().sort_index().reset_index()
        ev_by_year.columns = ["year", "count"]
        ev_by_year.to_csv(out_tables / "ev_adoption_by_year.csv", index=False)

        plt.figure()
        plt.plot(ev_by_year["year"], ev_by_year["count"], marker="o")
        plt.title("EV Adoption by Year")
        plt.xlabel("Year")
        plt.ylabel("Count")
        save_plot(out_plots / "ev_adoption_by_year.png")

    # Range by state
    if ev_state and ev_range:
        top_states = ev[ev_state].value_counts().head(10).index.tolist()
        sub = ev[ev[ev_state].isin(top_states)].copy()

        sub["_range"] = pd.to_numeric(sub[ev_range], errors="coerce")

        stats = (
            sub.groupby(ev_state)["_range"]
            .describe()[["count", "mean", "50%", "min", "max"]]
            .reset_index()
        )
        stats.columns = [
            "state", "count", "mean_range", "median_range", "min_range", "max_range"
        ]
        stats.to_csv(out_tables / "ev_range_by_state_top10.csv", index=False)

        # Boxplot
        plt.figure()
        data_for_box = [
            pd.to_numeric(ev[ev[ev_state] == st][ev_range], errors="coerce").dropna()
            for st in top_states
        ]
        plt.boxplot(data_for_box, labels=top_states, showfliers=False)
        plt.xticks(rotation=45, ha="right")
        plt.title("EV Range Distribution by State (Top 10)")
        plt.xlabel("State")
        plt.ylabel("Electric Range")
        save_plot(out_plots / "ev_range_distribution_by_state_top10.png")

    print("Full pipeline complete. Output saved to:", out_base)


if __name__ == "__main__":
    main()
