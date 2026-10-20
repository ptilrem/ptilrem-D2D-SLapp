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
    "The Electricity Transfers page displays daily energy summaries prepared in "
    "Jupyter with Spark and stored in MongoDB Atlas. Until ENTSO-E API access is approved, "
    "the displayed values are clearly labeled synthetic demonstration data."
)

st.info("Use the sidebar to navigate between pages.")
