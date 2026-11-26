
"""Project background, data sources, methods, and useful links."""

import streamlit as st

st.title("About This Project", icon=":material/info:")

st.write(
    "The Norwegian Electricity Dashboard is part of a project in IND320 (Data to Decision)."
    "The project is developed across four assignments,"
    "expanding from simple data visualizations into an interactive dashboard "
    "combining energy statistics, weather data, and statistical analysis."
)

st.divider()

# Explain how the dashboard has developed.
st.subheader("Project Development", icon=":material/history:")

st.markdown(
    "**Assignment 1 — Reservoir Statistics**  \n"
    "Explored Norwegian hydropower reservoir data and built the initial "
    "Streamlit dashboard using a locally stored dataset.\n\n"
    "**Assignment 2 — APIs and Databases**  \n"
    "Integrated the NVE API and added cross-border electricity-transfer "
    "data using Spark, Cassandra, and MongoDB Atlas.\n\n"
    "**Assignment 3 — Weather and Time-Series Analysis**  \n"
    "Added geographic sampling, historical ERA5 weather data, anomaly "
    "detection, STL decomposition, and spectrogram analysis."
)

st.divider()

# Describe the data sources and analysis methods.
st.subheader("Reservoir Statistics", icon=":material/water_drop:")

st.write(
    "The Norwegian Water Resources and Energy Directorate (NVE) publishes "
    "weekly reservoir filling statistics. The dashboard retrieves these "
    "measurements directly from the NVE Magasinstatistikk API."
)

st.write(
    "Users can explore reservoir data for electricity areas (EL), "
    "the nationwide total (NO), and watershed regions (VASS). "
    "The dashboard provides tables, interactive plots, and two "
    "additional time-series analyses:"
)

st.markdown(
    "- **STL decomposition:** Separates reservoir filling into "
    "long-term trend, seasonal patterns, and residual variation.\n"
    "- **Spectrogram:** Shows how the strength of different repeating "
    "cycles changes over time."
)

st.subheader("Electricity Transfers", icon=":material/electric_bolt:")

st.write(
    "Cross-border electricity-transfer measurements are retrieved from "
    "the ENTSO-E Transparency Platform. The dataset covers nine "
    "international connections in both directions over two years."
)

st.write(
    "Apache Spark and Cassandra are used to process the measurements "
    "and calculate daily energy totals. The aggregated data is stored "
    "in MongoDB Atlas and displayed through interactive Streamlit charts."
)

st.subheader("Weather Analysis", icon=":material/partly_cloudy_day:")

st.write(
    "Geographic boundaries from NVE Atlas were used to generate "
    "1,000 random coordinates in each of eight Norwegian regions. "
    "Historical hourly temperature and precipitation measurements "
    "are retrieved from Open-Meteo's ERA5 dataset."
)

st.write(
    "For 2024, saved weather datasets represent averages across "
    "100 sampled locations in NO1, NO2, and NO3. Other regions "
    "use smaller live API samples, depending on availability."
)

st.markdown(
    "- **DCT and SPC:** Separate slower precipitation variation "
    "from short-term fluctuations and highlight statistical outliers.\n"
    "- **Local Outlier Factor (LOF):** Identifies unusual hourly "
    "temperature observations based on their neighbouring values."
)

st.caption(
    "Weather measurements represent sampled regional averages. "
    "Live requests may be affected by Open-Meteo API limits."
)

st.divider()

# Links to the original data sources and project repository.
st.subheader("Useful Links", icon=":material/link:")

st.markdown(
    "- [GitHub Repository](https://github.com/ptilrem/ptilrem-D2D-SLapp)\n"
    "- [NVE Magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/magasinstatistikk/)\n"
    "- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)\n"
    "- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)"
)
