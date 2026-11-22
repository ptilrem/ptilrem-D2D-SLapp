"""Home page for the Norwegian Electricity Dashboard."""

import streamlit as st

st.title("⚡ Norwegian Electricity Dashboard")
st.write(
    "Explore Norwegian hydropower reservoir statistics and "
    "cross-border electricity transfers using real energy data."
)

st.divider()

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("💧 Reservoir Statistics")
        st.caption("NVE Magasinstatistikk API")

        st.write(
            "Explore weekly Norwegian reservoir measurements, "
            "compare regions, and investigate seasonal patterns."
        )

        st.markdown("**Explore:**")
        st.page_link(
            "pages/reservoir_table.py",
            label="📋 Reservoir Data Table"
        )
        st.page_link(
            "pages/reservoir_plots.py",
            label="📈 Reservoir Data Plots"
        )
        st.page_link(
            "pages/reservoir_analysis.py",
            label="🌊 Reservoir Analysis"
        )

        st.caption(
            "Select EL, NO, or VASS to explore different area types."
        )

with right:
    with st.container(border=True):
        st.subheader("⚡ Electricity Transfers")
        st.caption("ENTSO-E / MongoDB Atlas")

        st.write(
            "Explore electricity imports and exports "
            "between Norway and neighbouring countries."
        )

        st.markdown("**Explore:**")
        st.page_link(
            "pages/electricity_transfers.py",
            label="📊 Cross-border Electricity Transfers"
        )

        st.caption(
            "Energy data processed with Spark and Cassandra, "
            "then stored in MongoDB Atlas."
        )

with st.container(border=True):
    st.subheader("🌦️ Weather Analysis")
    st.caption("Open-Meteo ERA5 Historical Weather")

    st.write(
        "Explore historical temperature and precipitation across "
        "Norwegian regions. Detect precipitation outliers using "
        "DCT/SPC and temperature anomalies using Local Outlier Factor."
    )

    st.page_link(
        "pages/weather_analysis.py",
        label="🌦️ Explore Weather Analysis"
    )

    st.caption(
        "Select a region and adjust the analysis parameters "
        "to investigate unusual weather observations."
    )

st.divider()

st.page_link("pages/about.py", label="ℹ️ About This Project")
st.caption("You can also use the sidebar to navigate between pages.")