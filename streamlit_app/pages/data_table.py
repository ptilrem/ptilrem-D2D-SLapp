# Import necessary libraries
import streamlit as st
import pandas as pd
from utils.dataLoader import DataLoader

# Set title of the page
st.title("📋 Data Table")
st.write("Placeholder - table view of the reservior data")

# Use the DataLoader class to load the reservoir data
loader = DataLoader()
df = loader.load()

# Isolate the first calendar month present in the dataset
first_date = df['date_id'].min()
first_month_mask = (
    (df['date_id'].dt.year == first_date.year) 
& (df['date_id'].dt.month == first_date.month)
)

df_first_month = df[first_month_mask]

st.write(f"Showing data for: {first_date.strftime('%B %Y')}")

# Build one row per measurement column, where each row's Trend cell holds
# the list of values for that column across the first month of data
table_data = {
    'Column': [],
    'Trend (first month)': [],
}

for col in loader.get_measurement_columns():
    table_data['Column'].append(col.replace('_', ' ').title())
    table_data['Trend (first month)'].append(df_first_month[col].tolist())

display_df = pd.DataFrame(table_data)

st.dataframe(
    display_df,
    column_config={
        'Trend (first month)': st.column_config.LineChartColumn(
            'Trend (first month)',
            help='Values across the first calendar month of data',
        ),
    },
    hide_index=True,
    use_container_width=True,
)

st.caption("Note: The data includes all regions/area types for this exercise, so there are multiple values per week")