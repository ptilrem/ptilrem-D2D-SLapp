import pandas as pd
import streamlit as st

class DataLoader:
    """
    Handles reading and preparing the data for the app.
    Putting it into a class allows for a smoother transition
    to MongoDB in the future, and only requires changes in the class
    rather than throughout the other scripts.
    """

    # Dictionary for translating the column names from Norwegian to English
    # Copied from the Jupyter notebook part of the assignment (see notebook/assignment1.ipynb)
    column_rename_dict = {
    'dato_Id': 'date_id',
    'omrType': 'area_type',
    'omrnr': 'area_number',
    'iso_aar': 'iso_year',
    'iso_uke': 'iso_week',
    'fyllingsgrad': 'fill_percentage',
    'kapasitet_TWh': 'capacity_TWh',
    'fylling_TWh': 'stored_energy_TWh', # Unsure. Energifylling: Described as capacity times fill percentage
    'neste_Publiseringsdato': 'next_publish_date',
    'fyllingsgrad_forrige_uke': 'fill_percentage_last_week',
    'endring_fyllingsgrad': 'change_fill_percentage'
}

    # The measurements worth plotting (float values).
    # This exludes the identifiers and classifiers
    # Copied from the Jupyter notebook part of the assignment (see notebook/assignment1.ipynb)
    measurement_columns = [
    'fill_percentage',
    'capacity_TWh',
    'stored_energy_TWh',
    'fill_percentage_last_week',
    'change_fill_percentage',
]

    # Path default is set to the reservoirs.csv file, however it can be changed to any other path if specified
    def __init__(self, csv_path: str = 'data/reservoirs.csv'):
        self.csv_path = csv_path

    @st.cache_data
    def load(_self) -> pd.DataFrame:
        """
        Reads the CSV file, renames columns to english, 
        converts dates to datetime format, and sorts the data chronologically.
        Data is cached so the file is only read once per session,
        rather than every time a widget is interacted with.
        """
        df = pd.read_csv(_self.csv_path)
        df = df.rename(columns=_self.column_rename_dict)
        df['date_id'] = pd.to_datetime(df['date_id'])
        df = df.sort_values(by='date_id')
        return df

    def get_measurement_columns(self) -> list:
        """
        Returns the list of measurement columns that can be plotted.
        Keeping this command here makes it easier to change the names later
        if we think the translations are off and needs updating. This way
        the pages don't get hard coded with the column names so we only need
        to change it here.
        """
        return self.measurement_columns
