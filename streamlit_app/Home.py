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
home_page = st.Page("pages/page1_home_content.py", title="Home", icon="🏠", default=True)
table_page = st.Page("pages/page2_data_table.py", title="Data Table", icon="📋")
plot_page = st.Page("pages/page3_data_plot.py", title="Data Plot", icon="📈")
about_page = st.Page("pages/page4_about.py", title="About", icon="ℹ️")

# Order the pages in the sidebar
pgs = st.navigation([home_page, table_page, plot_page, about_page])
pgs.run()