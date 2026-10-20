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
    """Read Spark-prepared daily energy values; prefer real over demo data."""
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client["ind320_assignment2"]
    real = list(db["entsoe_daily_flows"].find({}, {"_id": 0}))
    if real:
        return real, False
    return list(db["entsoe_daily_flows_demo"].find({}, {"_id": 0})), True


try:
    rows, is_demo = load_daily_flows(mongodb_uri)
except Exception:
    st.error("MongoDB could not be reached. Check database credentials and Atlas network access.")
    st.stop()

if not rows:
    st.info("No electricity-flow data in MongoDB yet. Run Section 8 of the notebook.")
    st.stop()

flows = pd.DataFrame(rows)
flows["date"] = pd.to_datetime(flows["date_utc"], utc=True)
flows["year"] = flows["year"].astype(int)
flows["month"] = flows["month"].astype(int)
flows["energy_mwh"] = pd.to_numeric(flows["energy_mwh"])

# Avoid confusing synthetic demonstration figures with measured transfers.
if is_demo:
    st.warning("SYNTHETIC DEMONSTRATION — fictional data, not actual electricity transfers.")
else:
    st.caption("Source: ENTSO-E Transparency Platform, processed using Spark")

left, right = st.columns(2)
with left:
    st.subheader("Annual transfers: into vs. out of Norway")
    connection = st.radio("Connection", sorted(flows["connection"].unique()))
    year = st.selectbox("Year", sorted(flows["year"].unique(), reverse=True))
    chosen = flows[(flows["connection"] == connection) & (flows["year"] == year)]
    totals = chosen.groupby("direction", as_index=False)["energy_mwh"].sum()
    if not totals.empty and totals["energy_mwh"].sum() > 0:
        fig = px.pie(totals, values="energy_mwh", names="direction", hole=0,
                     title=f"{connection} — {year}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No measurements for this connection/year.")

with right:
    st.subheader("Daily transferred energy")
    months = st.pills(
        "Choose months", options=list(range(1, 13)), default=[1],
        selection_mode="multi", format_func=lambda month: month_abbr[month]
    )
    selected = flows[(flows["year"] == year) & flows["month"].isin(months or [])].copy()
    if selected.empty:
        st.info("Choose months that contain observations.")
    else:
        # One series for each connection and flow direction, as in the notebook.
        selected["Series"] = selected["connection"] + " — " + selected["direction"]
        fig = px.line(selected.sort_values("date"), x="date", y="energy_mwh", color="Series",
                      title=f"Daily flow energy ({year})",
                      labels={"date": "Date (UTC)", "energy_mwh": "Energy per day (MWh)"})
        st.plotly_chart(fig, use_container_width=True)

with st.expander("About these data"):
    st.write("Source: ENTSO-E Transparency Platform, Cross-Border Physical Flows (A11).")
    st.write("The Jupyter Notebook stores readings in Cassandra through Spark, calculates daily transferred energy (MWh), and uploads summaries to MongoDB Atlas.")
    st.write("The pie chart compares energy transferred into and out of Norway, not electricity production.")
    st.write(f"Dates available: {flows['date'].min().date()} to {flows['date'].max().date()}.")
    if is_demo:
        st.write("These are synthetic demonstration values while ENTSO-E API access is pending.")