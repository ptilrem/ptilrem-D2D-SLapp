"""Weather analysis using historical Open-Meteo ERA5 data."""

import streamlit as st
from pathlib import Path
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor
from datetime import date

st.title("Weather Analysis", icon=":material/partly_cloudy_day:")
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

# Download and average historical ERA5 weather for the selected region.
@st.cache_data
def load_weather(region, start_date, end_date, n_locations):
    # Use saved 100-location ERA5 data when available.
    saved_file = (
        Path(__file__).resolve().parents[2]
        / "data"
        / f"weather_{region}_2024_100locations.parquet"
    )

    # Reuse saved data only when the settings match exactly.
    if (
        start_date == date(2024, 1, 1)
        and end_date == date(2024, 12, 31)
        and n_locations == 100
        and saved_file.exists()
    ):
        return pd.read_parquet(saved_file), 100

    # Prevent accidentally requesting excessive amounts of API data.
    if start_date > end_date:
        raise ValueError("The start date must be before the end date.")

    days = (end_date - start_date).days + 1

    if days * n_locations > 2000:
        raise ValueError(
            "This request is too large. Choose fewer locations "
            "or a shorter date range."
        )

    if region == "Norway":
        # Sample equally from the five electricity regions.
        points = locations[
            locations["area"].str.startswith("NO")
        ].groupby("area").head(n_locations // 5)
    else:
        points = locations[locations["area"] == region].head(n_locations)

    params = {
        "latitude": ",".join(points["latitude"].astype(str)),
        "longitude": ",".join(points["longitude"].astype(str)),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
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

    return weather, len(points)


# Let users explicitly load weather data instead of downloading automatically.
st.subheader("Weather Data Settings", icon=":material/tune:")


with st.form("weather_settings"):
    st.caption(f"Selected region: {region}")

    # Choose the period of historical weather data.
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start date",
            value=date(2024, 1, 1)
        )

    with col2:
        end_date = st.date_input(
            "End date",
            value=date(2024, 12, 31)
        )

    # Choose how many sampled coordinates to use.
    n_locations = st.selectbox(
        "Number of locations",
        options=[5, 10, 25, 50, 100],
        index=4 if region in ["NO1", "NO2", "NO3"] else 0
    )

    load_clicked = st.form_submit_button(
        "Load weather data",
        icon=":material/download:"
    )


if load_clicked:
    try:
        with st.spinner("Loading historical ERA5 weather data..."):
            weather, n_locations = load_weather(
                region, start_date, end_date, n_locations
            )

        # Keep the results when users adjust the analysis sliders.
        st.session_state["weather_result"] = {
            "region": region,
            "weather": weather,
            "n_locations": n_locations
        }

    except (requests.RequestException, ValueError) as error:
        st.error(f"Could not load weather data: {error}")
        st.stop()

# Only display analyses when data for the selected region is available.
result = st.session_state.get("weather_result")

if result is None or result["region"] != region:
    st.info("Click 'Load weather data' to display the analyses.")
    st.stop()

weather = result["weather"]
n_locations = result["n_locations"]

st.caption(
    f"Region: {region}. Hourly ERA5 data averaged over {n_locations} "
    f"of {len(region_points):,} sampled locations."
)


# Prepare the weather measurements for the analysis plots.
hourly_weather = weather.rename(columns={
    "precipitation": "precipitation_mm",
    "temperature_2m": "temperature_c"
}).copy()

hourly_weather["time"] = pd.to_datetime(
    hourly_weather["time"], utc=True
)

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

    precipitation = hourly_weather["precipitation_mm"].to_numpy()

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
    outliers = hourly_weather.loc[
        mask, ["time", "precipitation_mm"]
    ]

    # Display precipitation, SPC boundaries and detected outliers.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        hourly_weather["time"],
        precipitation,
        label="Hourly precipitation"
    )
    ax.plot(hourly_weather["time"], lower, "--", label="Lower SPC boundary")
    ax.plot(hourly_weather["time"], upper, "--", label="Upper SPC boundary")
    ax.scatter(
        outliers["time"],
        outliers["precipitation_mm"],
        color="red",
        label="Outliers",
        zorder=3
    )

    ax.set_title(f"Precipitation Outliers — {region} (2024)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Precipitation (mm per hour)")
    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.metric("Outliers detected", len(outliers))
    st.dataframe(outliers, hide_index=True)

with lof_tab:
    st.subheader("Temperature Anomalies — LOF")

    # Choose the expected proportion of anomalies.
    outlier_fraction = st.slider(
        "Outlier proportion",
        0.01, 0.10, 0.01, 0.01,
        format="%.2f"
    )

    # Detect unusual temperatures using Local Outlier Factor.
    lof = LocalOutlierFactor(
        n_neighbors=20,
        contamination=outlier_fraction
    )

    mask = lof.fit_predict(hourly_weather[["temperature_c"]]) == -1
    anomalies = hourly_weather.loc[
        mask, ["time", "temperature_c"]
    ]

    # Plot daily temperatures and highlight anomalies.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        hourly_weather["time"],
        hourly_weather["temperature_c"],
        label="Hourly temperature"
    )
    ax.scatter(
        anomalies["time"],
        anomalies["temperature_c"],
        color="red",
        label="Anomalies",
        zorder=3
    )

    ax.set_title(f"Temperature Anomalies — {region} (2024)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.metric("Anomalies detected", len(anomalies))
    st.dataframe(anomalies, hide_index=True)