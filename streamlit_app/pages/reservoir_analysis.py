"""STL and spectrogram analysis of NVE reservoir data."""

import streamlit as st
from utils.dataLoader import DataLoader
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL

st.title("💧 Reservoir Analysis")

# Reuse the NVE data loader from the existing reservoir pages.
df = DataLoader().load()

# Share the selected area type with the other reservoir pages.
area_options = ["EL", "NO", "VASS"]
saved_area = st.session_state.get("nve_area_type", "EL")

area_type = st.radio(
    "Area type",
    area_options,
    index=area_options.index(saved_area),
    horizontal=True
)

st.session_state["nve_area_type"] = area_type

# Select an area number within the chosen area type.
df = df[df["area_type"] == area_type].copy()

area_numbers = sorted(df["area_number"].astype(int).unique())
area_number = st.selectbox("Area number", area_numbers)

df = df[df["area_number"] == area_number].copy()

# Two tabs for the required reservoir analyses.
stl_tab, spectrogram_tab = st.tabs([
    "STL Decomposition",
    "Spectrogram"
])

with stl_tab:
    st.subheader("Seasonal-Trend Decomposition")

    # Allow users to adjust the STL parameters.
    seasonal = st.slider("Seasonal smoother", 7, 51, 13, step=2)
    trend = st.slider("Trend smoother", 55, 155, 101, step=2)
    robust = st.checkbox("Robust fitting", value=True)

    # Prepare a regular weekly reservoir filling series.
    filling = (
        df.set_index("date_id")["fill_percentage"]
        .astype(float)
        .resample("W-SUN")
        .mean()
        .interpolate()
    )

    # Decompose the data using a 52-week seasonal cycle.
    result = STL(
        filling,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust
    ).fit()

    fig = result.plot()
    fig.set_size_inches(12, 9)
    fig.suptitle(f"STL Decomposition — {area_type} {area_number}")
    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

with spectrogram_tab:
    st.subheader("Spectrogram")
    st.write("Spectrogram analysis will appear here.")