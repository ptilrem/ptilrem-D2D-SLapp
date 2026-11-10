"""Assignment context and project links, moved from the original fourth page."""
import streamlit as st

st.title("ℹ️ About This Project")
st.write(
    "This app is part of IND320's four-part course project. It explores weekly "
    "Norwegian hydropower reservoir statistics and cross-border electricity transfers."
)

st.subheader("Reservoir statistics")
st.write(
    "NVE publishes weekly statistics for nationwide, electricity-area (EL) "
    "and watershed-area (VASS) groupings. The app now reads the NVE API "
    "directly instead of the CSV file used in Assignment 1."
)

st.subheader("Transfer statistics")
st.write(
    "The notebook retrieves real cross-border electricity transfers from the "
    "ENTSO-E Transparency Platform, covering nine international connections "
    "in both directions over two years. Spark stores the measurements in "
    "Cassandra and calculates daily energy totals, which are uploaded to "
    "MongoDB Atlas for visualization in this Streamlit app."
)

st.subheader("Links")
st.markdown(
    "- [NVE Magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/magasinstatistikk/)\n"
    "- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)\n"
    "- [GitHub repository](https://github.com/ptilrem/ptilrem-D2D-SLapp)"
)
