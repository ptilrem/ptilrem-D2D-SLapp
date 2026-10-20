# Import necessary libraries
import pandas as pd
import requests
import streamlit as st


class DataLoader:
    """Keep API access and data preparation in one place for all NVE pages."""

    api_url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

    # Preserve the English column names used in Assignment 1.
    column_rename_dict = {
        "dato_Id": "date_id",
        "omrType": "area_type",
        "omrnr": "area_number",
        "iso_aar": "iso_year",
        "iso_uke": "iso_week",
        "fyllingsgrad": "fill_percentage",
        "kapasitet_TWh": "capacity_TWh",
        "fylling_TWh": "stored_energy_TWh",
        "neste_Publiseringsdato": "next_publish_date",
        "fyllingsgrad_forrige_uke": "fill_percentage_last_week",
        "endring_fyllingsgrad": "change_fill_percentage",
    }

    measurement_columns = [
        "fill_percentage",
        "capacity_TWh",
        "stored_energy_TWh",
        "fill_percentage_last_week",
        "change_fill_percentage",
    ]

    @st.cache_data(ttl=3600)
    def load(_self) -> pd.DataFrame:
        """Download NVE data, rename columns, parse dates, and sort observations."""
        response = requests.get(DataLoader.api_url, timeout=90)
        response.raise_for_status()
        df = pd.DataFrame(response.json()).rename(columns=DataLoader.column_rename_dict)

        # ISO year/week gives a usable Monday date if date_id is absent.
        iso_monday = pd.to_datetime(
            df["iso_year"].astype(str) + "-W" +
            df["iso_week"].astype(str).str.zfill(2) + "-1",
            format="%G-W%V-%u", errors="coerce",
        )
        if "date_id" in df.columns:
            df["date_id"] = pd.to_datetime(df["date_id"], errors="coerce").fillna(iso_monday)
        else:
            df["date_id"] = iso_monday

        df["area_number"] = pd.to_numeric(df["area_number"], errors="coerce")
        for column in DataLoader.measurement_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        # The API may represent fill as a fraction, e.g. 0.7 = 70%.
        for column in ["fill_percentage", "fill_percentage_last_week", "change_fill_percentage"]:
            if df[column].abs().max() <= 1.05:
                df[column] *= 100

        # Do not filter to NO: the assignment requires EL, NO and VASS.
        return df.dropna(subset=["date_id", "area_number"]).sort_values("date_id")

    def get_measurement_columns(self) -> list:
        """Return the five measurement names used in the table and plots."""
        return self.measurement_columns

