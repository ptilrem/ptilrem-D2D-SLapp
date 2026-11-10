"""Weather analysis using historical Open-Meteo ERA5 data."""

import streamlit as st
from pathlib import Path
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import dct, idct

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

# Download and average historical ERA5 weather for the selected region.
@st.cache_data
def load_weather(region):
    if region == "Norway":
        # Use one location from each electricity region.
        points = locations[
            locations["area"].str.startswith("NO")
        ].groupby("area").head(1)
    else:
        points = locations[locations["area"] == region].head(5)

    params = {
        "latitude": ",".join(points["latitude"].astype(str)),
        "longitude": ",".join(points["longitude"].astype(str)),
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "hourly": "temperature_2m,precipitation",
        "models": "era5",
        "timezone": "UTC"
    }

    response = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params=params,
        timeout=120
    )
    response.raise_for_status()

    results = response.json()
    if isinstance(results, dict):
        results = [results]

    # Calculate the hourly average across the sampled locations.
    frames = [pd.DataFrame(result["hourly"]) for result in results]
    weather = (
        pd.concat(frames)
        .groupby("time", as_index=False)[["temperature_2m", "precipitation"]]
        .mean()
    )
    weather["time"] = pd.to_datetime(weather["time"], utc=True)

    return weather

# Load the selected region's weather data.
with st.spinner("Loading historical ERA5 weather data..."):
    weather = load_weather(region)

# Prepare daily weather measurements for the analysis plots.
daily_weather = (
    weather.set_index("time")
    .resample("D")
    .agg({
        "precipitation": "sum",
        "temperature_2m": "mean"
    })
    .reset_index()
)

daily_weather = daily_weather.rename(columns={
    "precipitation": "precipitation_mm",
    "temperature_2m": "temperature_c"
})

# TEMP TEST: Remove after verifying the daily aggregation.
st.caption(f"Daily weather observations: {len(daily_weather)}")

# Separate tabs for the two weather analyses.
spc_tab, lof_tab = st.tabs([
    "Precipitation — DCT/SPC",
    "Temperature — LOF"
])

with spc_tab:
    st.subheader("Precipitation Outliers — DCT/SPC")

    # Adjustable parameters for the outlier detection.
    cutoff = st.slider("DCT frequency cutoff", 1, 50, 12)
    n_std = st.slider("Standard deviations", 1.0, 5.0, 3.0, 0.5)

    precipitation = daily_weather["precipitation_mm"].to_numpy()

    # Remove slow variations using the Discrete Cosine Transform.
    coefficients = dct(precipitation, norm="ortho")
    coefficients[cutoff:] = 0
    trend = idct(coefficients, norm="ortho")
    satv = precipitation - trend

    # Calculate robust SPC boundaries using median and MAD.
    centre = np.median(satv)
    sigma = 1.4826 * np.median(np.abs(satv - centre))

    lower = trend + centre - n_std * sigma
    upper = trend + centre + n_std * sigma

    # Identify precipitation values outside the boundaries.
    mask = (precipitation < lower) | (precipitation > upper)
    outliers = daily_weather.loc[
        mask, ["time", "precipitation_mm"]
    ]

    # Display precipitation, SPC boundaries and detected outliers.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        daily_weather["time"],
        precipitation,
        label="Daily precipitation"
    )
    ax.plot(daily_weather["time"], lower, "--", label="Lower SPC boundary")
    ax.plot(daily_weather["time"], upper, "--", label="Upper SPC boundary")
    ax.scatter(
        outliers["time"],
        outliers["precipitation_mm"],
        color="red",
        label="Outliers",
        zorder=3
    )

    ax.set_title(f"Precipitation Outliers — {region} (2024)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Precipitation (mm/day)")
    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.metric("Outliers detected", len(outliers))
    st.dataframe(outliers, hide_index=True)

with lof_tab:
    st.subheader("Temperature Anomalies")
    st.write("Local Outlier Factor analysis will appear here.")