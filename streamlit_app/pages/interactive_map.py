"""Interactive map of Norwegian electricity price areas and regional data."""

import copy
import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


# -----------------------------------------------------------------------------
# Paths and map settings
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
GEOJSON_PATH = ROOT / "data" / "geojson" / "price_areas.geojson"
WEATHER_REGIONS = ["NO1", "NO2", "NO3"]  # Saved ERA5 data for 2024
WEATHER_MODES = ["Temperature", "Precipitation"]
MISSING_COLOR = [150, 150, 150, 100]

AREA_COLORS = {
    "NO1": [70, 130, 200, 140],
    "NO2": [65, 170, 130, 140],
    "NO3": [180, 115, 190, 140],
    "NO4": [230, 160, 65, 140],
    "NO5": [90, 175, 190, 140],
}


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_geojson(path):
    """Read the prepared electricity price-area boundaries."""
    with open(path, encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(ttl=3600)
def load_reservoir_filling():
    """Download NVE weekly reservoir filling for electricity price areas."""
    url = (
        "https://biapi.nve.no/magasinstatistikk/api/"
        "Magasinstatistikk/HentOffentligData"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = pd.DataFrame(response.json())

    data = data[data["omrType"] == "EL"].copy()
    data["date"] = pd.to_datetime(data["dato_Id"])
    for column in ["omrnr", "fyllingsgrad", "iso_aar", "iso_uke"]:
        data[column] = pd.to_numeric(data[column])

    return data


@st.cache_data
def load_weekly_weather():
    """Summarize the saved 2024 ERA5 observations by local ISO week."""
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

        # Average across locations at each hour, if the cache contains
        # multiple observations per hour. This also handles caches that
        # already contain a single regional mean per hour.
        hourly = (
            weather.groupby("time", as_index=False)
            [["temperature_2m", "precipitation"]]
            .mean()
        )

        iso = hourly["time"].dt.isocalendar()
        hourly["iso_year"] = iso.year
        hourly["iso_week"] = iso.week

        # Precipitation is the SUM of regional hourly means, not the sum
        # across individual weather locations.
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
# Colour functions
# -----------------------------------------------------------------------------
def filling_color(value):
    """Map a reservoir filling fraction (0–1) to an RGBA colour."""
    return [
        int(235 - 185 * value),
        int(110 + 55 * value),
        int(65 + 155 * value),
        140,
    ]


def weather_color(value, minimum, maximum, mode):
    """Map weather values to a consistent annual colour range."""
    span = maximum - minimum
    fraction = (value - minimum) / span if span > 0 else 0.5
    fraction = max(0, min(1, fraction))

    if mode == "Temperature":
        # Cold blue -> warm orange/red.
        return [
            int(60 + 175 * fraction),
            int(140 - 60 * fraction),
            int(230 - 165 * fraction),
            140,
        ]

    # Dry light grey -> wet blue.
    return [
        int(228 - 170 * fraction),
        int(229 - 85 * fraction),
        int(232 - 12 * fraction),
        140,
    ]


def show_color_legend(mode, minimum=None, maximum=None):
    """Display a colour legend matching the active map mode."""

    st.markdown("**Colour legend**")

    if mode == "Electricity price area":
        values = list(AREA_COLORS.items())
        colors = [color for _, color in values]
        labels = [region for region, _ in values]

    else:
        if mode == "Reservoir filling":
            values = [0, 0.25, 0.5, 0.75, 1]
            colors = [filling_color(value) for value in values]
            labels = [f"{value:.0%}" for value in values]

        else:
            if minimum is None or maximum is None:
                return

            values = [
                minimum + (maximum - minimum) * i / 4
                for i in range(5)
            ]

            colors = [
                weather_color(value, minimum, maximum, mode)
                for value in values
            ]

            unit = "°C" if mode == "Temperature" else "mm"
            labels = [f"{value:.1f} {unit}" for value in values]

    columns = st.columns(5)

    for column, color, label in zip(columns, colors, labels):
        red, green, blue, alpha = color

        with column:
            st.markdown(
                f"""
                <div style="
                    background-color: rgba(
                        {red}, {green}, {blue}, {alpha / 255}
                    );
                    height: 20px;
                    border-radius: 4px;
                "></div>
                """,
                unsafe_allow_html=True
            )
            st.caption(label)

    if mode in WEATHER_MODES:
        st.caption(
            "Grey regions have no saved weather measurements. "
            "Weather colours use the same scale across 2024."
        )


# -----------------------------------------------------------------------------
# Page controls and selected week's data
# -----------------------------------------------------------------------------
st.title("Interactive Map", icon=":material/map:")
st.write(
    "Explore Norwegian electricity price areas, reservoir filling, "
    "and historical weather."
)

price_areas = load_geojson(str(GEOJSON_PATH))

if "map_selected_region" not in st.session_state:
    st.session_state["map_selected_region"] = None

try:
    reservoir_data = load_reservoir_filling()
except (requests.RequestException, ValueError) as error:
    st.error(f"Could not load reservoir statistics: {error}")
    st.stop()

color_mode = st.radio(
    "Colour areas by",
    [
        "Reservoir filling",
        "Electricity price area",
        "Temperature",
        "Precipitation",
    ],
    horizontal=True,
)

# Only read ERA5 files when a weather mode is active.
weekly_weather = pd.DataFrame()
date_source = reservoir_data

if color_mode in WEATHER_MODES:
    weekly_weather = load_weekly_weather()
    if weekly_weather.empty:
        st.warning("No saved weather data is available.")
        st.stop()

    # Restrict the date selector to NVE weeks with saved 2024 weather.
    weather_weeks = (
        weekly_weather.loc[
            weekly_weather["iso_year"] == 2024, ["iso_year", "iso_week"]
        ]
        .drop_duplicates()
    )
    date_source = reservoir_data.merge(
        weather_weeks,
        left_on=["iso_aar", "iso_uke"],
        right_on=["iso_year", "iso_week"],
        how="inner",
    )

available_dates = sorted(date_source["date"].dropna().unique(), reverse=True)
if not available_dates:
    st.warning("No matching reservoir and weather weeks found.")
    st.stop()

selected_date = st.selectbox(
    "Reservoir reporting week",
    options=available_dates,
    format_func=lambda date: pd.Timestamp(date).strftime("%d %B %Y"),
)

weekly_data = reservoir_data[reservoir_data["date"] == selected_date]
filling_by_area = weekly_data.set_index("omrnr")["fyllingsgrad"].to_dict()

selected_iso_year = int(weekly_data["iso_aar"].iloc[0])
selected_iso_week = int(weekly_data["iso_uke"].iloc[0])

weather_by_area = {}
weather_min = weather_max = None

if color_mode in WEATHER_MODES:
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

    # Fix the scale across 2024 so a colour means the same in every week.
    full_series = weekly_weather.loc[
        weekly_weather["iso_year"] == 2024, property_column
    ].dropna()
    weather_min = float(full_series.min())
    weather_max = float(full_series.max())


# -----------------------------------------------------------------------------
# Attach colours and values to GeoJSON features
# -----------------------------------------------------------------------------
colored_areas = copy.deepcopy(price_areas)

for feature in colored_areas["features"]:
    region = feature["properties"]["region"]
    area_number = int(region.replace("NO", ""))
    filling = filling_by_area.get(area_number)

    if color_mode == "Electricity price area":
        fill_color = AREA_COLORS[region]
        label = region

    elif color_mode == "Reservoir filling":
        if filling is not None and pd.notna(filling):
            fill_color = filling_color(filling)
            label = f"{filling:.1%}"
        else:
            fill_color = MISSING_COLOR
            label = "No data"

    else:
        value = weather_by_area.get(region)
        if value is not None and pd.notna(value):
            fill_color = weather_color(
                value, weather_min, weather_max, color_mode
            )
            unit = "°C" if color_mode == "Temperature" else "mm"
            label = f"{value:.1f} {unit}"
        else:
            fill_color = MISSING_COLOR
            label = "No weather data"

    feature["properties"]["fill_color"] = fill_color
    feature["properties"]["value_label"] = label


# -----------------------------------------------------------------------------
# Map layers and selection highlighting
# -----------------------------------------------------------------------------
layer = pdk.Layer(
    "GeoJsonLayer",
    data=colored_areas,
    id="price-areas",
    filled=True,
    stroked=True,
    pickable=True,
    auto_highlight=True,
    get_fill_color="properties.fill_color",
    get_line_color=[40, 70, 110, 255],
    line_width_min_pixels=2,
)
layers = [layer]

selected_region = st.session_state["map_selected_region"]
if selected_region is not None:
    selected_features = [
        feature for feature in price_areas["features"]
        if feature["properties"]["region"] == selected_region
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
        latitude=64.5,
        longitude=14.0,
        zoom=3.7,
        pitch=0,
    ),
    map_style=None,
    tooltip={"text": "Area: {region}\nValue: {value_label}"},
)

event = st.pydeck_chart(
    deck,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-object",
    key="price_area_map",
)

selected_indices = event.selection.indices.get("price-areas", [])
if selected_indices:
    selected_index = selected_indices[0]
    region = price_areas["features"][selected_index]["properties"]["region"]
    if region != st.session_state["map_selected_region"]:
        st.session_state["map_selected_region"] = region
        st.rerun()


# -----------------------------------------------------------------------------
# Feedback and source notes
# -----------------------------------------------------------------------------
if st.session_state["map_selected_region"]:
    st.success(
        f"Selected electricity area: {st.session_state['map_selected_region']}"
    )
else:
    st.info("Click an electricity area on the map to select it.")

show_color_legend(
    color_mode,
    minimum=weather_min,
    maximum=weather_max
)

if color_mode == "Reservoir filling":
    st.caption(
        "Orange indicates lower reservoir filling; blue indicates higher filling."
    )
elif color_mode == "Electricity price area":
    st.caption("Each colour identifies a different electricity price area.")
elif color_mode == "Temperature":
    st.caption(
        "Blue indicates colder weeks; orange/red indicates warmer weeks. "
        "Grey regions have no saved ERA5 weather data."
    )
else:
    st.caption(
        "Light grey indicates drier weeks; blue indicates wetter weeks. "
        "Grey regions without measurements have no saved ERA5 weather data."
    )

st.caption(
    "Electricity price-area boundaries: NVE Atlas. "
    "Reservoir filling: NVE Magasinstatistikk. "
    "Weather: Open-Meteo ERA5 (saved 2024 observations for NO1–NO3). "
    "The first and last ISO weeks of the weather archive may be incomplete."
)
