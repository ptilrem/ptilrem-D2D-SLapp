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

    