# Import necessary libraries
import streamlit as st

# This step is not really necessary as Streamlit will automatically put
# the files under 'pages/' into the sidebar, but it allows for more 
# control over the order and names of the pages. It also allows for 
# more customization in the future, and also keeps the file names cleaner imo
st.set_page_config(
    page_title = "Assignment Dashboard",
    page_icon=":material/electric_bolt:",
    layout = "wide" # Makes the app use the full width of the browser
)

# Set up the pages with icons titles for the side bar
home = st.Page("pages/home_content.py", title="Home", icon=":material/home:", default=True)
map_page = st.Page("pages/interactive_map.py", title="Interactive Map", icon=":material/map:")
table = st.Page("pages/reservoir_table.py", title="Reservoir Table", icon=":material/table_chart:")
plots = st.Page("pages/reservoir_plots.py", title="Reservoir Plots", icon=":material/monitoring:")
analysis = st.Page("pages/reservoir_analysis.py",title="Reservoir Analysis", icon=":material/water_drop:")
weather = st.Page("pages/weather_analysis.py", title="Weather Analysis", icon=":material/partly_cloudy_day:")
flows = st.Page("pages/electricity_transfers.py", title="Cross-border Electricity Transfers", icon=":material/electric_bolt:")
about = st.Page("pages/about.py", title="About", icon=":material/info:")

# Order the pages in the sidebar
navigation = st.navigation([home, map_page, table, plots, analysis, weather, flows, about])
navigation.run()