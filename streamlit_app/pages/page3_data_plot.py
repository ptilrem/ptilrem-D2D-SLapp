"""NVE plots grouped by area type and area number."""
# Import necessary libraries
import plotly.express as px
import streamlit as st
from utils.dataLoader import DataLoader

st.title("📈 Reservoir Data Plots")
loader = DataLoader()

try:
    df = loader.load()
except Exception as exc:
    st.error(f"Could not load NVE data: {exc}")
    st.stop()

area_type = st.radio("Area type", ["EL", "NO", "VASS"], horizontal=True)
df = df[df["area_type"] == area_type].copy()
if df.empty:
    st.info("No data for this area type.")
    st.stop()

# Choose which months from NVE's response to display on both reservoir pages.
df["year_month"] = df["date_id"].dt.strftime("%Y-%m")
months = sorted(df["year_month"].unique().tolist())
previous = st.session_state.get("nve_month_range", (months[0], months[0]))
if previous[0] not in months or previous[1] not in months:
    previous = (months[0], months[0])
month_range = st.select_slider(
    "Select month interval", options=months, value=previous
)
st.session_state["nve_month_range"] = month_range
st.caption("The API provides the full history; the slider selects which records are shown.")

columns = loader.get_measurement_columns()
measurement = st.selectbox(
    "Measurement", ["All measurements"] + columns,
    format_func=lambda x: x.replace("_", " ").title(),
)
selected = df[df["year_month"].between(*month_range)].copy()
if selected.empty:
    st.info("No measurements for the selected interval.")
    st.stop()

# Every individual area number gets its own line.
selected["Area"] = area_type + " " + selected["area_number"].astype(int).astype(str)
plot_columns = columns if measurement == "All measurements" else [measurement]
for column in plot_columns:
    figure = px.line(
        selected, x="date_id", y=column, color="Area",
        title=column.replace("_", " ").title(),
        labels={"date_id": "Date", column: column.replace("_", " ").title()},
    )
    st.plotly_chart(figure, use_container_width=True)