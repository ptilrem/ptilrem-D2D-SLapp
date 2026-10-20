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
    "The notebook uses Spark to store raw electricity-transfer data in Cassandra, "
    "aggregate daily energy, and upload the resulting records to MongoDB Atlas "
    "for this Streamlit app. Synthetic demonstration data are used until "
    "ENTSO-E approves API access."
)

st.subheader("Links")
st.markdown(
    "- [NVE Magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/magasinstatistikk/)\n"
    "- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)\n"
    "- [GitHub repository](https://github.com/ptilrem/ptilrem-D2D-SLapp)"
)
