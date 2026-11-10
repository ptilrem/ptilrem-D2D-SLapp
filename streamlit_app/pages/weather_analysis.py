"""Weather analysis using historical Open-Meteo ERA5 data."""

import streamlit as st

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