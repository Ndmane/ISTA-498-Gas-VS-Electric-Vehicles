import pandas as pd
import numpy as np
import re
import plotly.express as px
from pathlib import Path

# PATHS
cars_path = "Cars_Datasets_2025.csv"
ev_path = "Electric_Vehicle_Population_Data.csv"
out_dir = Path("denis_clean_outputs")
out_dir.mkdir(exist_ok=True, parents=True)

# SAFE FILE READING

def safe_read(file_path):
    for enc in ["latin1", "utf-8", "cp1252"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"Loaded: {file_path} ({df.shape[0]} rows) [{enc}]")
            return df
        except:
            continue
    raise RuntimeError(f"Could not read: {file_path}")

cars = safe_read(cars_path)
ev = safe_read(ev_path)

# UNIVERSAL CLEANER
def clean_numeric(series):
    def parse(x):
        if pd.isna(x):
            return np.nan
        x = str(x).lower().replace(",", "").replace("$", "")
        x = re.sub(r"[^0-9\-.]", " ", x)
        nums = re.findall(r"\d+(?:\.\d+)?", x)
        if not nums:
            return np.nan
        vals = [float(n) for n in nums]
        return np.mean(vals)
    return series.map(parse)

# CLEAN: GAS CARS
cars = cars.rename(columns={
    "Cars Prices": "price_usd",
    "HorsePower": "horsepower",
    "Total Speed": "top_speed",
    "Performance(0 - 100 )KM/H": "acceleration",
    "Fuel Types": "fuel_type"
})

# Normalize fuel type text
if "fuel_type" in cars.columns:
    cars["fuel_type"] = (
        cars["fuel_type"]
        .astype(str)
        .str.lower()
        .replace({
            "petrol": "gas",
            "gasoline": "gas",
            "benzin": "gas",
            "unknown": "other"
        })
    )

for col in ["price_usd", "horsepower", "top_speed", "acceleration"]:
    if col in cars.columns:
        cars[col] = clean_numeric(cars[col])

cars = (
    cars.drop_duplicates()
        .dropna(subset=["price_usd", "horsepower"])
        .query("1000 < price_usd < 300000")
)

# CLEAN: EV DATA
ev = ev.rename(columns={
    "Base MSRP": "price_usd",
    "Electric Range": "range_miles",
    "Make": "make",
    "Model": "model"
})

for col in ["price_usd", "range_miles"]:
    ev[col] = clean_numeric(ev[col])

ev = (
    ev.drop_duplicates()
        .dropna(subset=["price_usd", "range_miles"])
        .query("range_miles > 20 and 1000 < price_usd < 300000")
)

print("\n🧹 CLEANING COMPLETE")
print(f"Cars rows: {cars.shape[0]}")
print(f"EV rows: {ev.shape[0]}")

# 1. PRICE COMPARISON

avg_prices = pd.DataFrame({
    "Type": ["Gas Cars", "Electric Cars"],
    "Average Price ($)": [
        cars["price_usd"].mean(),
        ev["price_usd"].mean()
    ]
})

fig1 = px.bar(
    avg_prices,
    x="Type", y="Average Price ($)",
    title="Average Price Comparison: Gas vs Electric",
    text_auto=".0f",
    color="Type",
    color_discrete_sequence=["#1f77b4", "#2ca02c"]
)
fig1.update_traces(textposition="outside")
fig1.write_html(out_dir / "average_price_comparison.html")
fig1.show()

# 2. EV RANGE DISTRIBUTION

fig2 = px.histogram(
    ev, x="range_miles", nbins=35,
    title="EV Range Distribution",
    color_discrete_sequence=["#17becf"]
)
fig2.add_vline(
    x=ev["range_miles"].mean(), line_dash="dash", line_color="red",
    annotation_text="Mean", annotation_position="top right"
)
fig2.add_vline(
    x=ev["range_miles"].median(), line_dash="dot", line_color="blue",
    annotation_text="Median", annotation_position="top left"
)
fig2.write_html(out_dir / "ev_range_distribution.html")
fig2.show()

# 3. HORSEPOWER VS PRICE (GAS CARS)

fig3 = px.scatter(
    cars, x="horsepower", y="price_usd",
    color="fuel_type",
    hover_data=["Company Names", "Cars Names"],
    title="Gas Cars: Horsepower vs Price",
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig3.update_traces(marker=dict(size=6, opacity=0.7))
fig3.write_html(out_dir / "horsepower_vs_price.html")
fig3.show()

# 4. TOP 10 EV BRANDS BY AVG RANGE

if "make" in ev.columns:
    ev_avg = (
        ev.groupby("make")["range_miles"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig4 = px.bar(
        ev_avg, x="make", y="range_miles",
        color="range_miles", color_continuous_scale="Viridis",
        title="Top EV Brands by Average Range",
        labels={"make": "Brand", "range_miles": "Avg Range (miles)"}
    )
    fig4.update_layout(xaxis={'categoryorder':'total descending'})
    fig4.write_html(out_dir / "top_ev_brands.html")
    fig4.show()

print("\n All charts generated successfully.")
print("Saved in folder: denis_clean_outputs")
