# Import necessary libraries
import streamlit as st

# This step is not really necessary as Streamlit will automatically put
# the files under 'pages/' into the sidebar, but it allows for more 
# control over the order and names of the pages. It also allows for 
# more customization in the future, and also keeps the file names cleaner imo
st.set_page_config(
    page_title = "Assignment Dashboard",
    page_icon = "🏠",
    layout = "wide" # Makes the app use the full width of the browser
)

# Set up the pages with icons titles for the side bar
home = st.Page("pages/home_content.py", title="Home", icon="🏠", default=True)
table = st.Page("pages/data_table.py", title="Reservoir Table", icon="📋")
plots = st.Page("pages/data_plot.py", title="Reservoir Plots", icon="📈")
analysis = st.Page("pages/reservoir_analysis.py",title="Reservoir Analysis", icon="💧")
weather = st.Page("pages/weather_analysis.py", title="Weather Analysis", icon="🌦️")
flows = st.Page("pages/electricity_transfers.py", title="Cross-border Electricity Transfers", icon="📊")
about = st.Page("pages/about.py", title="About", icon="ℹ️")

# Order the pages in the sidebar
navigation = st.navigation([home, table, plots, analysis, weather, flows, about])
navigation.run()