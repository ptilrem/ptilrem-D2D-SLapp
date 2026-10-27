# Import necessary libraries
import streamlit as st

# Set title and page text
st.title("🏠 Norwegian Electricity Dashboard")
st.write("Explore Norwegian reservoir statistics and cross-border electricity transfers!")

st.subheader("Reservoir statistics (NVE)")
st.write(
    "The Reservoir Table and Reservoir Plots pages download weekly observations "
    "directly from the NVE Magasinstatistikk API. Choose EL, NO or VASS "
    "to compare the corresponding regions."
)

st.subheader("Cross-border transfers (ENTSO-E / MongoDB)")
st.write(
    "The Electricity Transfers page displays real cross-border electricity data "
    "from the ENTSO-E Transparency Platform. The measurements are processed "
    "using Spark, stored in Cassandra, and aggregated into daily energy totals "
    "before being uploaded to MongoDB Atlas."
)

st.info("Use the sidebar to navigate between pages.")
