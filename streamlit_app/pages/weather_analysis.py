"""Weather analysis using historical Open-Meteo ERA5 data."""

import streamlit as st
from pathlib import Path
import pandas as pd

st.title("🌦️ Weather Analysis")
st.write(
    "Explore precipitation outliers and temperature anomalies "
    "using historical ERA5 weather data."
)

# Reuse the area type selected on the reservoir pages.
area_options = ["EL", "NO", "VASS"]
saved_area = st.session_state.get("nve_area_type", "EL")

area_type = st.radio(
    "Area type",
    area_options,
    index=area_options.index(saved_area),
    horizontal=True
)

st.session_state["nve_area_type"] = area_type

# Load the coordinates generated in Assignment 3 notebook
@st.cache_data
def load_locations():
    path = Path(__file__).resolve().parents[2] / "data" / "region_locations.parquet"
    return pd.read_parquet(path)


locations = load_locations()

# Match the selected reservoir area to its sampled weather locations.
if area_type == "EL":
    area_number = st.selectbox("Area number", [1, 2, 3, 4, 5])
    region = f"NO{area_number}"

elif area_type == "VASS":
    area_number = st.selectbox("Area number", [1, 2, 3])
    region = {1: "East", 2: "West", 3: "North"}[area_number]

else:
    region = "Norway"

# Select the coordinates belonging to the chosen region.
if region == "Norway":
    region_points = locations[locations["area"].str.startswith("NO")]
else:
    region_points = locations[locations["area"] == region]

st.caption(f"Selected region: {region} — {len(region_points):,} sampled locations")

# Separate tabs for the two weather analyses.
spc_tab, lof_tab = st.tabs([
    "Precipitation — DCT/SPC",
    "Temperature — LOF"
])

with spc_tab:
    st.subheader("Precipitation Outliers")
    st.write("DCT and SPC analysis will appear here.")

with lof_tab:
    st.subheader("Temperature Anomalies")
    st.write("Local Outlier Factor analysis will appear here.")