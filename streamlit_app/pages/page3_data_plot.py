# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dataLoader import DataLoader

# Set title
st.title("📈 Data Plot")

# Load the data
loader = DataLoader()
df = loader.load()

# Create the options for the slider by using the unique years and months
df['year_month'] = df['date_id'].dt.to_period('M').astype(str)
slider_options = sorted(df['year_month'].unique())

st.subheader("Filter options")

# Creates the options for the drop-down menu, making the "All columns" option,
# and importing the other columns from the DataLoader class.
# The format_funct function removes underscores and capitalizes the first letter of each word
# to make the drop-down menu nicer to look at
column_choice = st.selectbox(
    "Select a measurement to plot",
    options=["All Columns"] + loader.get_measurement_columns(),
    format_func=lambda x: x if x == "All Columns" else x.replace('_', ' ').title()
    )

# Sets the options for the slider and the default value to the first month
slider_range = st.select_slider(
    "Select month range to plot",
    options=slider_options,
    value=(slider_options[0], slider_options[0])
    )

# Filter for the selected month range
mask = (df['year_month'] >= slider_range[0]) & (df['year_month'] <= slider_range[1])
df_filtered = df[mask]

range_label = f"{slider_range[0]} to {slider_range[1]}"

# Plot the data using Plotly Express with the selected columns
if column_choice == "All Columns":
    fig = px.line(
        df_filtered,
        x='date_id',
        y=loader.get_measurement_columns(),
        title=f'All measurements from {range_label}',
        labels={'value': 'Value', 'date_id': 'Date', 'variable': 'Metric'},
    )
else:
    fig = px.line(
        df_filtered, x='date_id', y=column_choice,
        title=f'{column_choice.replace("_", " ").title()} from {range_label}',
        labels={column_choice: column_choice.replace('_', ' ').title(), 'date_id': 'Date'},
    )

# Display the plot in the Streamlit app
st.plotly_chart(fig, use_container_width=True)