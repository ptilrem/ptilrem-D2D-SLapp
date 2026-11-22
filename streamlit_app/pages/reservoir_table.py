"""NVE table showing first-month trends for each area number."""
# Import necessary libraries
import pandas as pd
import streamlit as st
from utils.dataLoader import DataLoader

st.title("📋 Reservoir Data Table")
loader = DataLoader()

try:
    df = loader.load()
except Exception as exc:
    st.error(f"Could not load NVE data: {exc}")
    st.stop()


# Remember the selected area type across reservoir pages.
area_options = ["EL", "NO", "VASS"]
saved_area = st.session_state.get("nve_area_type", "EL")

area_type = st.radio(
    "Area type",
    area_options,
    index=area_options.index(saved_area),
    horizontal=True
)

st.session_state["nve_area_type"] = area_type

df = df[df["area_type"] == area_type].copy()

# The plots page stores the selected month interval in session state.
df["year_month"] = df["date_id"].dt.strftime("%Y-%m")
months = sorted(df["year_month"].unique().tolist())
if not months:
    st.info("No data for this area type.")
    st.stop()
start, end = st.session_state.get("nve_month_range", (months[0], months[0]))
selected = df[df["year_month"].between(start, end)]
if selected.empty:
    st.info("No data in this date interval. Choose another range on Reservoir Plots.")
    st.stop()

first_month = selected["year_month"].min()
first_month_data = selected[selected["year_month"] == first_month]
st.write(f"First month of selected interval: **{first_month}**")

# One row for each measurement and area number; values become mini line charts.
rows = []
for area_number, area_rows in first_month_data.groupby("area_number"):
    area_rows = area_rows.sort_values("date_id")
    for column in loader.get_measurement_columns():
        rows.append({
            "Area number": int(area_number),
            "Measurement": column.replace("_", " ").title(),
            "Trend": area_rows[column].dropna().tolist(),
        })

st.dataframe(
    pd.DataFrame(rows),
    column_config={"Trend": st.column_config.LineChartColumn("Trend")},
    hide_index=True,
    use_container_width=True,
)
