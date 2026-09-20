# Import necessary libraries
import streamlit as st

# Set title and page text
st.title("ℹ️ About This Project")

st.write(
    """
    This dashboard explores weekly reservoir fill data from Norway's
    hydropower system, published by NVE (Norges vassdrags- og
    energidirektorat — the Norwegian Water Resources and Energy
    Directorate). It's part of a semester-long, four-part assignment,
    where each part builds on the last — starting with a local CSV file
    here, and eventually moving to a live database.
    """
)

st.subheader("What is 'fill percentage'?")
st.write(
    """
    Norway generates most of its electricity from hydropower, stored in
    roughly 490 reservoirs monitored weekly by NVE. The **fill
    percentage** (*fyllingsgrad*) tells you how full these reservoirs
    are relative to their total capacity — a key indicator of Norway's
    power supply situation. A low fill percentage going into winter,
    for example, can signal tighter electricity supply and higher
    prices.
    """
)

st.subheader("About the data")
st.write(
    """
    The dataset includes weekly measurements broken down three ways:
    nationally, by electricity price area (5 regions), and by watershed
    area (3 regions) — meaning each week actually contains 9 separate
    data points across these groupings. For this stage of the project,
    the data is shown unfiltered; regional filtering is a planned
    feature for a future iteration.
    """
)

st.subheader("Links")
st.markdown(
    """
    - 📊 [Data source: NVE Magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/om-magasinstatistikken/)
    - 💻 [GitHub repository](https://github.com/yourusername/your-repo-name)
    """
)

st.caption("Built with Python, Pandas, and Streamlit.")