# ptilrem-D2D-SLapp

- Version: 3.0
- Author: ptilrem

# Assignment Dashboard

**IND320 · Assignment 3** | [Live Streamlit app](https://ptilrem-d2d-slapp.streamlit.app/) | [GitHub repository](https://github.com/ptilrem/ptilrem-D2D-SLapp)

A Streamlit dashboard for exploring Norwegian hydropower reservoirs, cross-border electricity transfers, and historical weather data.

This project was developed for IND320 (Data to Decision) at NMBU. It is built incrementally across four assignments, with each part extending the same Python notebooks and Streamlit application.

## Features

- **Reservoir Table:** Explore weekly Norwegian hydropower reservoir statistics from NVE.
- **Reservoir Plots:** Visualize reservoir measurements across selected dates and areas.
- **Electricity Transfers:** Examine cross-border import and export data using interactive charts. The data is read from MongoDB Atlas; the project has also used clearly identified synthetic demonstration records where ENTSO-E access was unavailable.
- **Reservoir Analysis:** Explore seasonal patterns with **STL decomposition** and changing frequencies with a **spectrogram**.
- **Weather Analysis:** Analyze historical precipitation with **DCT-based filtering and statistical process control (SPC)**, and detect unusual temperatures using **Local Outlier Factor (LOF)**.

The app supports NVE area selections for electricity areas (**EL**), nationwide (**NO**) and watershed groupings (**VASS**) where applicable, along with adjustable parameters for the analyses.

## Project development

| Assignment | Main additions |
| --- | --- |
| **1** | Initial reservoir dataset exploration, plots and Streamlit dashboard, using locally stored NVE data. |
| **2** | Direct NVE API integration and cross-border electricity-transfer processing using Spark, Cassandra and MongoDB Atlas. |
| **3** | Geographic sampling, historical ERA5 weather, DCT/SPC and LOF anomaly detection, STL decomposition, spectrograms and two additional Streamlit analysis pages. |

## Data sources and methodology

**NVE reservoir statistics:** Weekly filling measurements are retrieved from the [NVE Magasinstatistikk API](https://www.nve.no/energi/analyser-og-statistikk/magasinstatistikk/).

**NVE Atlas geographic data:** Electricity price-area polygons (NO1–NO5) and regional polygons are used to generate **1,000 random coordinates per area**. The northern polygons (RM and RN) and eastern polygons (RØ and RS) are combined, producing **8,000 sampled coordinates across eight areas**. These coordinates are stored in Parquet format for reuse.

**Open-Meteo ERA5:** Historical hourly temperature and precipitation are retrieved from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api). For the 2024 analysis, **100 sampled locations each for NO1, NO2 and NO3** were downloaded in batches, averaged by hour and saved locally. Other area selections can use smaller live API requests. Open-Meteo usage limits can affect these requests.

**Analysis resolution:** The submitted Part 3 weather analyses use daily precipitation totals and daily mean temperatures derived from the hourly ERA5 observations. Updating SPC and LOF to operate directly on hourly observations is a planned improvement following TA feedback.

**Electricity transfers:** The cross-border data workflow uses the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/), Apache Spark, Cassandra and MongoDB Atlas. Where actual ENTSO-E measurements were unavailable, the project used labeled demonstration data rather than presenting it as real measurements.

## Project structure

```
├── data/                       # Geographic files and cached Parquet datasets
├── notebook/
│   ├── assignment1.ipynb
│   ├── assignment2.ipynb
│   └── assignment3.ipynb
├── streamlit_app/
│   ├── Home.py                 # Navigation and page configuration
│   ├── pages/                  # Home, data views and analysis pages
│   ├── utils/
│   │   └── dataLoader.py      # Shared NVE data loading and preparation
│   └── .streamlit/
│       └── config.toml         # App theme settings
├── requirements.txt
└── README.md
```

## Run the app locally

```bash
git clone https://github.com/ptilrem/ptilrem-D2D-SLapp.git
cd ptilrem-D2D-SLapp
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run streamlit_app/Home.py
```
Some features require network access to public APIs. The electricity-transfer page also requires valid MongoDB connection credentials in Streamlit secrets; credentials must not be committed to the repository.

## Branches

- `main` — the submitted version under review.
- `dev` — ongoing improvements, merged into main after review.

Each branch has its own deployed Streamlit app, so ongoing work never affects the version under review. Once an assignment is approved, `dev` is merged into `main`.