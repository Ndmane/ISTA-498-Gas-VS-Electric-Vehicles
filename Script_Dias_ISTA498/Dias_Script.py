"""
Dias Akhmadiev — Final Full Integrated Analysis Script
Electric vs Gas Cars — Interactive Graphs, Data Cleaning, and Visualization
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import mplcursors

# --- Enable GUI pop-up windows ---
try:
    plt.switch_backend("TkAgg")
except Exception:
    pass
plt.ion()

ROOT = Path(".")
OUT = ROOT / "dias_outputs"
PLOTS = OUT / "plots"
OUT.mkdir(exist_ok=True, parents=True)
PLOTS.mkdir(exist_ok=True, parents=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def safe_read(paths, encodings=("latin1","utf-8","cp1252")):
    for p in paths:
        for enc in encodings:
            try:
                df = pd.read_csv(p, encoding=enc)
                log(f"Loaded: {p} (encoding={enc}) shape={df.shape}")
                return df
            except Exception:
                continue
    raise RuntimeError("Failed to load dataset.")

# --- Load datasets ---
cars = safe_read(["Cars_Datasets_2025.csv", "Cars Datasets 2025.csv"])
ev = safe_read(["Electric_Vehicle_Population_Data.csv", "Electric Vehicle Population Data.csv"])

# --- Improved numeric cleaner ---
def to_numeric(series):
    def parse(x):
        if pd.isna(x): return np.nan
        if isinstance(x, (int, float)): return float(x)
        if not isinstance(x, str): return np.nan
        x = x.strip().replace("–", "-").replace(",", "").replace("$", "").replace(" ", "")
        if "-" in x:
            try:
                a, b = x.split("-")
                return (float(a) + float(b)) / 2
            except:
                return np.nan
        try:
            return float(x)
        except:
            return np.nan
    return series.map(parse)

# --- Clean columns ---
cars = cars.rename(columns={
    "Cars Prices": "price_usd",
    "HorsePower": "horsepower",
    "Total Speed": "top_speed",
    "Performance(0 - 100 )KM/H": "zero_to_100_kmh",
    "CC/Battery Capacity": "capacity"
})

for c in ["price_usd","horsepower","top_speed","zero_to_100_kmh","capacity"]:
    if c in cars.columns:
        cars[c] = to_numeric(cars[c])

ev = ev.rename(columns={
    "Electric Range": "ev_range_miles",
    "Base MSRP": "ev_msrp",
    "Make": "make",
    "Model": "model",
    "Model Year": "model_year"
})

for c in ["ev_range_miles","ev_msrp","model_year"]:
    if c in ev.columns:
        ev[c] = to_numeric(ev[c])

# --- Remove incorrect or unrealistic values ---
if "price_usd" in cars.columns:
    cars = cars[(cars["price_usd"] > 1000) & (cars["price_usd"] < 300000)]

if "ev_msrp" in ev.columns:
    ev = ev[(ev["ev_msrp"] > 1000) & (ev["ev_msrp"] < 300000)]

if "ev_range_miles" in ev.columns:
    ev = ev[ev["ev_range_miles"] > 30]

log(f"After cleaning: Cars={len(cars)}, EVs={len(ev)}")

# --- Print basic statistics ---
if "price_usd" in cars.columns:
    print("\nGas Cars Price Summary:\n", cars["price_usd"].describe())

if "ev_msrp" in ev.columns:
    print("\nElectric Cars Price Summary:\n", ev["ev_msrp"].describe())

# --- TCO functions ---
def annual_energy_cost_ev(miles, kwh_100mi, price_kwh):
    return miles * (kwh_100mi/100) * price_kwh

def annual_energy_cost_ice(miles, mpg, price_gal):
    return (miles/mpg) * price_gal if mpg > 0 else np.nan

def tco_curve(price, miles, years, maint, func, **kw):
    total, result = price, []
    for _ in range(years):
        total += maint + func(miles, **kw)
        result.append(total)
    return result

A = {
    "years": 10,
    "annual_miles": 12000,
    "ev_kwh_100mi": 28,
    "ice_mpg": 30,
    "price_kwh": 0.14,
    "price_gal": 3.8,
    "maint_ev": 450,
    "maint_ice": 800,
    "ev_price": np.nanmedian(ev["ev_msrp"]) if "ev_msrp" in ev.columns else 47000,
    "ice_price": np.nanmedian(cars["price_usd"]) if "price_usd" in cars.columns else 32000
}

years = list(range(1, A["years"]+1))
ev_tco = tco_curve(A["ev_price"], A["annual_miles"], A["years"], A["maint_ev"],
                   annual_energy_cost_ev, kwh_100mi=A["ev_kwh_100mi"], price_kwh=A["price_kwh"])
ice_tco = tco_curve(A["ice_price"], A["annual_miles"], A["years"], A["maint_ice"],
                    annual_energy_cost_ice, mpg=A["ice_mpg"], price_gal=A["price_gal"])
breakeven = next((i+1 for i in range(len(years)) if ev_tco[i] <= ice_tco[i]), None)

def safe_show(fig, name):
    plt.draw()
    plt.pause(0.1)
    fig.savefig(PLOTS / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.show(block=True)

# --- 1. EV Price vs Range (Interactive) ---
if {"ev_range_miles","ev_msrp"}.issubset(ev.columns):
    fig = plt.figure(figsize=(8,6))
    sc = plt.scatter(ev["ev_range_miles"], ev["ev_msrp"], alpha=0.6, c="tab:blue", edgecolors="none")
    plt.title("EV Market Overview: Price vs Range")
    plt.xlabel("Range (miles)")
    plt.ylabel("Base MSRP ($)")
    plt.grid(alpha=0.3)

    # Hover labels
    labels = ev.get("model", ev.get("Model", pd.Series(["Unknown"] * len(ev)))).fillna("Unknown").astype(str)
    cursor = mplcursors.cursor(sc, hover=True)
    @cursor.connect("add")
    def on_hover(sel):
        idx = sel.index
        sel.annotation.set_text(
            f"{labels.iloc[idx]}\n"
            f"Range: {ev['ev_range_miles'].iloc[idx]} mi\n"
            f"Price: ${ev['ev_msrp'].iloc[idx]:,.0f}"
        )
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    safe_show(fig, "ev_price_vs_range")

# --- 2. Price Distribution (KDE) ---
fig = plt.figure(figsize=(8,5))
sns.kdeplot(data=cars, x="price_usd", fill=True, color="tab:orange", label="Gas Cars", alpha=0.4)
sns.kdeplot(data=ev, x="ev_msrp", fill=True, color="tab:blue", label="Electric Cars", alpha=0.4)
plt.title("Price Distribution: Gas vs Electric Cars")
plt.xlabel("Price ($)")
plt.ylabel("Density")
plt.legend()
plt.grid(alpha=0.3)
safe_show(fig, "price_distribution_kde")

# --- 3. Total Cost of Ownership (Interactive) ---
fig = plt.figure(figsize=(8,5))
ev_line, = plt.plot(years, ev_tco, label="EV TCO", linewidth=2.2, color="tab:blue")
ice_line, = plt.plot(years, ice_tco, label="ICE TCO", linewidth=2.2, color="tab:orange")

plt.xlabel("Years of Ownership")
plt.ylabel("Total Cost ($)")
plt.title("Total Cost of Ownership: EV vs ICE")
plt.legend()
plt.grid(alpha=0.3)

if breakeven:
    plt.axvline(breakeven, linestyle="--", alpha=0.7, color="gray")
    plt.text(
        breakeven + 0.2,
        (ev_tco[breakeven-1] + ice_tco[breakeven-1]) / 2,
        f"Breakeven ~ Year {breakeven}",
        fontsize=9
    )

# Hover interaction
cursor = mplcursors.cursor([ev_line, ice_line], hover=True)
@cursor.connect("add")
def on_hover(sel):
    year = years[int(sel.index)]
    ev_val = ev_tco[int(sel.index)]
    ice_val = ice_tco[int(sel.index)]
    sel.annotation.set_text(
        f"Year {year}\nEV: ${ev_val:,.0f}\nICE: ${ice_val:,.0f}"
    )
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

safe_show(fig, "tco_comparison")

print("\n✅ Analysis complete! Check dias_outputs/plots for saved images.")
input("Press Enter to close all windows...")
plt.close("all")
