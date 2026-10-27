"""MongoDB daily cross-border flow charts: annual pie and selected-month lines."""
from calendar import month_abbr
import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient

st.title("⚡ Cross-border Electricity Transfers")

# Production credentials must be entered in Streamlit Cloud's Secrets settings.
try:
    mongodb_uri = st.secrets["MONGODB_URI"]
except (FileNotFoundError, KeyError):
    st.error("Set MONGODB_URI in Streamlit secrets to enable this page.")
    st.stop()


@st.cache_data(ttl=600)
def load_daily_flows(uri):
    """Load real ENTSO-E daily electricity transfers from MongoDB."""
    with MongoClient(uri, serverSelectionTimeoutMS=10000) as client:
        return list(
            client["ind320_assignment2"]["entsoe_daily_flows"]
            .find({}, {"_id": 0})
        )


try:
    rows = load_daily_flows(mongodb_uri)
except Exception:
    st.error("MongoDB could not be reached. Check database credentials and Atlas network access.")
    st.stop()

if not rows:
    st.info("No ENTSO-E data found in MongoDB.")
    st.stop()

flows = pd.DataFrame(rows)
flows["date"] = pd.to_datetime(flows["date_utc"], utc=True)
flows["year"] = flows["year"].astype(int)
flows["month"] = flows["month"].astype(int)
flows["energy_mwh"] = pd.to_numeric(flows["energy_mwh"])

st.caption("Source: ENTSO-E Transparency Platform, processed using Spark")

left, right = st.columns(2)
with left:
    st.subheader("Annual transfers: into vs. out of Norway")

    # Select an international electricity connection.
    connection = st.radio(
        "Connection",
        sorted(flows["connection"].unique())
    )

    # Default to 2025, the complete calendar year.
    years = sorted(flows["year"].unique(), reverse=True)
    year = st.selectbox(
        "Year",
        years,
        index=years.index(2025) if 2025 in years else 0
    )

    # Show a note if the selected year is incomplete.
    year_dates = flows.loc[flows["year"] == year, "date"]
    first_date = year_dates.min().date()
    last_date = year_dates.max().date()

    if (
        first_date != pd.Timestamp(year, 1, 1).date()
        or last_date != pd.Timestamp(year, 12, 31).date()
    ):
        st.caption(f"Partial year: {first_date} to {last_date}.")

    # Calculate the total electricity transferred in each direction.
    chosen = flows[
        (flows["connection"] == connection) &
        (flows["year"] == year)
    ]

    totals = chosen.groupby(
        "direction", as_index=False
    )["energy_mwh"].sum()

    # Display the annual import/export comparison.
    if not totals.empty and totals["energy_mwh"].sum() > 0:
        fig = px.pie(
            totals,
            values="energy_mwh",
            names="direction",
            title=f"{connection} — {year}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No measurements for this connection/year.")

with right:
    st.subheader("Daily transferred energy")

    # Show only months available for the selected year.
    available_months = sorted(
        flows.loc[flows["year"] == year, "month"].unique().tolist()
    )

    # Select January by default, or the first available month.
    default_month = [1] if 1 in available_months else available_months[:1]

    months = st.pills(
        "Choose months",
        options=available_months,
        default=default_month,
        selection_mode="multi",
        format_func=lambda month: month_abbr[month]
    )

    # Filter the daily measurements by year and selected months.
    selected = flows[
        (flows["year"] == year) &
        (flows["month"].isin(months or []))
    ].copy()

    if selected.empty:
        st.info("Select a month to display electricity transfers.")
    else:
        # Display each connection and direction as a separate line.
        selected["Series"] = (
            selected["connection"] + " — " + selected["direction"]
        )

        fig = px.line(
            selected.sort_values("date"),
            x="date",
            y="energy_mwh",
            color="Series",
            title=f"Daily flow energy ({year})",
            labels={
                "date": "Date (UTC)",
                "energy_mwh": "Energy per day (MWh)"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

with st.expander("About these data"):
    st.write("Source: ENTSO-E Transparency Platform, Cross-Border Physical Flows (A11).")
    st.write("The Jupyter Notebook stores readings in Cassandra through Spark, calculates daily transferred energy (MWh), and uploads summaries to MongoDB Atlas.")
    st.write("The pie chart compares energy transferred into and out of Norway, not electricity production.")
    st.write(f"Dates available: {flows['date'].min().date()} to {flows['date'].max().date()}.")