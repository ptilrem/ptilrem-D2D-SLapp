"""Home page for the Norwegian Electricity Dashboard."""

import streamlit as st

st.title("⚡ Norwegian Electricity Dashboard")
st.write(
    "Explore Norwegian hydropower reservoir statistics and "
    "cross-border electricity transfers using real energy data."
)

st.divider()

# Introduce the two main parts of the dashboard.
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.subheader("💧 Reservoir Statistics")
        st.caption("NVE Magasinstatistikk API")

        st.write(
            "Explore weekly Norwegian reservoir measurements "
            "and compare different regions."
        )

        st.markdown("**Available pages:**")
        st.write("📋 Reservoir Data Table")
        st.write("📈 Reservoir Data Plots")

        st.caption(
            "Select EL, NO, or VASS to explore different area types."
        )

with right:
    with st.container(border=True):
        st.subheader("⚡ Electricity Transfers")
        st.caption("ENTSO-E Transparency Platform")

        st.write(
            "Explore real electricity imports and exports "
            "between Norway and neighbouring countries."
        )

        st.markdown("**Available page:**")
        st.write("📊 Cross-border Electricity Transfers")

        st.caption(
            "Data processed with Spark and Cassandra, "
            "then made available through MongoDB Atlas."
        )

st.divider()

st.info("👈 Use the sidebar to navigate between dashboard pages.")