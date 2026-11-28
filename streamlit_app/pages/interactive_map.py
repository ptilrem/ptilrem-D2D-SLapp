"""Interactive map of Norway's price areas, water areas, and weekly weather."""

import copy
import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
GEOJSON_DIR = ROOT / "data" / "geojson"
PRICE_GEOJSON_PATH = GEOJSON_DIR / "price_areas.geojson"
WATER_GEOJSON_PATH = GEOJSON_DIR / "water_areas.geojson"

WEATHER_REGIONS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
WEATHER_MODES = ["Temperature", "Precipitation"]
MISSING_COLOR = [150, 150, 150, 100]

AREA_COLORS = {
    "NO1": [70, 130, 200, 140],
    "NO2": [65, 170, 130, 140],
    "NO3": [180, 115, 190, 140],
    "NO4": [230, 160, 65, 140],
    "NO5": [90, 175, 190, 140],
}

# Instructor-provided shapefile grouped into three water areas.
# NVE Magasinstatistikk encodes these as VASS areas 1, 2 and 3.
WATER_AREA_NUMBERS = {"East": 1, "West": 2, "North": 3}


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_geojson(path):
    """Read a prepared GeoJSON boundary file."""
    with open(path, encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(ttl=3600)
def load_reservoir_filling():
    """Download NVE weekly reservoir filling for EL and VASS areas."""
    url = (
        "https://biapi.nve.no/magasinstatistikk/api/"
        "Magasinstatistikk/HentOffentligData"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = pd.DataFrame(response.json())

    data = data[data["omrType"].isin(["EL", "VASS"])].copy()
    data["date"] = pd.to_datetime(data["dato_Id"])
    for column in ["omrnr", "fyllingsgrad", "iso_aar", "iso_uke"]:
        data[column] = pd.to_numeric(data[column])

    return data


@st.cache_data
def load_weekly_weather():
    """Aggregate cached 2024 ERA5 observations to Norwegian ISO weeks."""
    weekly_frames = []

    for region in WEATHER_REGIONS:
        path = ROOT / "data" / f"weather_{region}_2024_100locations.parquet"
        if not path.exists():
            continue

        weather = pd.read_parquet(path)
        weather["time"] = (
            pd.to_datetime(weather["time"], utc=True)
            .dt.tz_convert("Europe/Oslo")
        )

        # Regional means: don't sum precipitation over 100 locations.
        hourly = (
            weather.groupby("time", as_index=False)[
                ["temperature_2m", "precipitation"]
            ]
            .mean()
        )
        iso = hourly["time"].dt.isocalendar()
        hourly["iso_year"] = iso.year
        hourly["iso_week"] = iso.week

        weekly = (
            hourly.groupby(["iso_year", "iso_week"], as_index=False)
            .agg(
                temperature_c=("temperature_2m", "mean"),
                precipitation_mm=("precipitation", "sum"),
            )
        )
        weekly["region"] = region
        weekly_frames.append(weekly)

    if not weekly_frames:
        return pd.DataFrame()
    return pd.concat(weekly_frames, ignore_index=True)


# -----------------------------------------------------------------------------
# Colour calculations and legend
# -----------------------------------------------------------------------------
def filling_color(value):
    """Colour a filling fraction between 0 and 1."""
    fraction = max(0, min(1, float(value)))
    return [
        int(235 - 185 * fraction),
        int(110 + 55 * fraction),
        int(65 + 155 * fraction),
        140,
    ]


def weather_color(value, minimum, maximum, mode):
    """Colour a weather measurement on a consistent annual scale."""
    span = maximum - minimum
    fraction = (value - minimum) / span if span > 0 else 0.5
    fraction = max(0, min(1, fraction))

    if mode == "Temperature":
        return [
            int(60 + 175 * fraction),
            int(140 - 60 * fraction),
            int(230 - 165 * fraction),
            140,
        ]
    return [
        int(228 - 170 * fraction),
        int(229 - 85 * fraction),
        int(232 - 12 * fraction),
        140,
    ]


def show_color_legend(mode, minimum=None, maximum=None):
    """Display swatches calculated with the same functions as the map."""
    st.markdown("**Colour legend**")

    if mode == "Electricity price area":
        labels = list(AREA_COLORS)
        colors = list(AREA_COLORS.values())
    elif mode == "Reservoir filling":
        values = [0, 0.25, 0.5, 0.75, 1]
        labels = [f"{value:.0%}" for value in values]
        colors = [filling_color(value) for value in values]
    else:
        if minimum is None or maximum is None:
            return
        values = [minimum + (maximum - minimum) * i / 4 for i in range(5)]
        units = "°C" if mode == "Temperature" else "mm"
        labels = [f"{value:.1f} {units}" for value in values]
        colors = [weather_color(value, minimum, maximum, mode) for value in values]

    for column, color, label in zip(st.columns(5), colors, labels):
        red, green, blue, alpha = color
        with column:
            st.markdown(
                f'<div style="background-color:rgba({red},{green},{blue},'
                f'{alpha / 255});height:20px;border-radius:4px"></div>',
                unsafe_allow_html=True,
            )
            st.caption(label)


# -----------------------------------------------------------------------------
# Page and selectors
# -----------------------------------------------------------------------------
st.title("Interactive Map", icon=":material/map:")
st.write(
    "Explore electricity price areas, grouped water areas, reservoir filling, "
    "and historical weather."
)

price_areas = load_geojson(str(PRICE_GEOJSON_PATH))
water_areas = load_geojson(str(WATER_GEOJSON_PATH))

# Preserve existing electricity-area selection for use on other pages.
if "map_selected_region" not in st.session_state:
    st.session_state["map_selected_region"] = None
if "map_selected_water_area" not in st.session_state:
    st.session_state["map_selected_water_area"] = None

boundary_mode = st.radio(
    "Geographic areas",
    ["Electricity price areas", "Water areas"],
    horizontal=True,
)
is_water = boundary_mode == "Water areas"

area_type = "VASS" if is_water else "EL"
map_areas = water_areas if is_water else price_areas
region_field = "water_area" if is_water else "region"
selection_key = "map_selected_water_area" if is_water else "map_selected_region"
layer_id = "water-areas" if is_water else "price-areas"

try:
    reservoir_data = load_reservoir_filling()
except (requests.RequestException, ValueError) as error:
    st.error(f"Could not load reservoir statistics: {error}")
    st.stop()

# The water-area mode has VASS filling measurements, but no cached weather
# observations for these grouped polygons; do not mislabel NO1–NO5 weather.
color_options = (
    ["Reservoir filling"]
    if is_water else
    ["Reservoir filling", "Electricity price area", "Temperature", "Precipitation"]
)
color_mode = st.radio("Colour areas by", color_options, horizontal=True)

# Keep EL and VASS measurements separate before choosing a date.
area_data = reservoir_data[reservoir_data["omrType"] == area_type]
weekly_weather = pd.DataFrame()
date_source = area_data

if color_mode in WEATHER_MODES:
    weekly_weather = load_weekly_weather()
    if weekly_weather.empty:
        st.warning("No saved weather data is available.")
        st.stop()

    weather_weeks = (
        weekly_weather.loc[
            weekly_weather["iso_year"] == 2024, ["iso_year", "iso_week"]
        ]
        .drop_duplicates()
    )
    date_source = area_data.merge(
        weather_weeks,
        left_on=["iso_aar", "iso_uke"],
        right_on=["iso_year", "iso_week"],
        how="inner",
    )

available_dates = sorted(date_source["date"].dropna().unique(), reverse=True)
if len(available_dates) == 0:
    st.warning(f"No available {area_type} reporting weeks found.")
    st.stop()

selected_date = st.selectbox(
    "Reservoir reporting week",
    options=available_dates,
    format_func=lambda date: pd.Timestamp(date).strftime("%d %B %Y"),
)

weekly_data = area_data[area_data["date"] == selected_date]
filling_by_area = weekly_data.set_index("omrnr")["fyllingsgrad"].to_dict()

weather_by_area = {}
weather_min = weather_max = None
if color_mode in WEATHER_MODES:
    selected_iso_year = int(weekly_data["iso_aar"].iloc[0])
    selected_iso_week = int(weekly_data["iso_uke"].iloc[0])
    property_column = (
        "temperature_c" if color_mode == "Temperature" else "precipitation_mm"
    )
    selected_weather = weekly_weather[
        (weekly_weather["iso_year"] == selected_iso_year)
        & (weekly_weather["iso_week"] == selected_iso_week)
    ]
    weather_by_area = (
        selected_weather.set_index("region")[property_column].to_dict()
    )
    full_series = weekly_weather.loc[
        weekly_weather["iso_year"] == 2024, property_column
    ].dropna()
    if not full_series.empty:
        weather_min = float(full_series.min())
        weather_max = float(full_series.max())


# -----------------------------------------------------------------------------
# Map colours and labels
# -----------------------------------------------------------------------------
colored_areas = copy.deepcopy(map_areas)
for feature in colored_areas["features"]:
    region = feature["properties"][region_field]
    area_number = (
        WATER_AREA_NUMBERS[region] if is_water else int(region.replace("NO", ""))
    )
    filling = filling_by_area.get(area_number)

    if color_mode == "Electricity price area":
        fill_color = AREA_COLORS[region]
        value_label = region
    elif color_mode == "Reservoir filling":
        if filling is not None and pd.notna(filling):
            fill_color = filling_color(filling)
            value_label = f"{filling:.1%}"
        else:
            fill_color = MISSING_COLOR
            value_label = "No data"
    else:
        value = weather_by_area.get(region)
        if value is not None and pd.notna(value) and weather_min is not None:
            fill_color = weather_color(value, weather_min, weather_max, color_mode)
            units = "°C" if color_mode == "Temperature" else "mm"
            value_label = f"{value:.1f} {units}"
        else:
            fill_color = MISSING_COLOR
            value_label = "No weather data"

    # Uniform tooltip property for both GeoJSON schemas.
    feature["properties"]["region"] = region
    feature["properties"]["fill_color"] = fill_color
    feature["properties"]["value_label"] = value_label


# -----------------------------------------------------------------------------
# Interactive map and persistent selection
# -----------------------------------------------------------------------------
layer = pdk.Layer(
    "GeoJsonLayer",
    data=colored_areas,
    id=layer_id,
    filled=True,
    stroked=True,
    pickable=True,
    auto_highlight=True,
    get_fill_color="properties.fill_color",
    get_line_color=[40, 70, 110, 255],
    line_width_min_pixels=2,
)
layers = [layer]

selected_region = st.session_state[selection_key]
if selected_region is not None:
    selected_features = [
        feature for feature in map_areas["features"]
        if feature["properties"][region_field] == selected_region
    ]
    if selected_features:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                data={"type": "FeatureCollection", "features": selected_features},
                id="selected-area-outline",
                filled=False,
                stroked=True,
                pickable=False,
                get_line_color=[255, 160, 50, 255],
                line_width_min_pixels=5,
            )
        )

deck = pdk.Deck(
    layers=layers,
    initial_view_state=pdk.ViewState(
        latitude=64.5, longitude=14.0, zoom=3.7, pitch=0
    ),
    map_style=None,
    tooltip={"text": "Area: {region}\nValue: {value_label}"},
)

event = st.pydeck_chart(
    deck,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-object",
    key="water_area_map" if is_water else "price_area_map",
)
selected_indices = event.selection.indices.get(layer_id, [])
if selected_indices:
    index = selected_indices[0]
    region = map_areas["features"][index]["properties"][region_field]
    if region != st.session_state[selection_key]:
        st.session_state[selection_key] = region
        st.rerun()

if st.session_state[selection_key]:
    label = "water area" if is_water else "electricity area"
    st.success(f"Selected {label}: {st.session_state[selection_key]}")
else:
    st.info("Click an area on the map to select it.")

show_color_legend(color_mode, weather_min, weather_max)

if color_mode == "Reservoir filling":
    st.caption("Orange indicates lower reservoir filling; blue indicates higher filling.")
elif color_mode == "Electricity price area":
    st.caption("Each colour identifies a different electricity price area.")
elif color_mode == "Temperature":
    st.caption("Blue indicates colder weeks; orange/red indicates warmer weeks.")
else:
    st.caption("Light grey indicates drier weeks; blue indicates wetter weeks.")

if is_water:
    st.caption(
        "Water-area polygons: East (RØ + RS), West (RV), North (RM + RN), "
        "combined from the shapefile supplied for the assignment. "
        "Filling values: NVE Magasinstatistikk VASS areas 1–3."
    )
else:
    st.caption(
        "Electricity price-area boundaries: NVE Atlas. "
        "Reservoir filling: NVE Magasinstatistikk. "
        "Weather: saved Open-Meteo ERA5 observations for NO1–NO5 (2024). "
        "First and last ISO weeks of the archive may be incomplete."
    )
