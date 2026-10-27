# ptilrem-D2D-SLapp

- Version: 2.0
- Author: ptilrem

# Assignment Dashboard

**IND320 · Assignment 2** | [Live Streamlit app](https://ptilrem-d2d-slapp.streamlit.app/) | [GitHub repository](https://github.com/ptilrem/ptilrem-D2D-SLapp)

A Streamlit dashboard for exploring Norwegian hydropower reservoirs and cross-border electricity transfers. This is part of a four-part course project, with each assignment building on the previous one.

## Features

- **Reservoir statistics:** Weekly data retrieved directly from the [NVE Magasinstatistikk API](https://www.nve.no/energi/analyser-og-statistikk/om-magasinstatistikken/). Explore EL, NO and VASS areas through interactive tables and plots.
- **Electricity transfers:** Real data from the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/), showing electricity flowing into and out of Norway. Compare annual totals and daily flows by connection, year and month.

## Data pipeline

- **NVE:** API → data preparation → Streamlit.
- **ENTSO-E:** API → Spark → Cassandra → daily aggregation → MongoDB Atlas → Streamlit.

The Jupyter notebooks contain the data processing, validation and visualizations. The Streamlit app presents the results interactively.

## Project structure

```
├── notebook/
│   └── assignment1.ipynb       # Data exploration, cleaning, and plotting from the assignment
├── streamlit_app/
│   ├── Home.py                 # Sets up page config and navigation
│   ├── pages/
│   │   ├── page1_home_content.py           # Home page content
│   │   ├── page2_data_table.py             # Data table view with LineChartColumn trends
│   │   ├── page3_data_plot.py              # Interactive plot with column/date-range filters
│   │   ├── page4_electricity_transfer.py   # Plots showing norwegian import/export of electricity     
│   │   └── page5_about.py                  # Project background, data source, and links etc.
│   ├── utils/
│   │   └── dataLoader.py             # DataLoader class: reads, renames, and prepares the data
│   └── .streamlit/
│       └── config.toml         # App theme settings
├── requirements.txt            # App dependencies
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
The electricity-transfer page requires MONGODB_URI to be configured in Streamlit secrets. Credentials and API tokens are not included in the repository.

## Branches

- `main` — the submitted version under review.
- `dev` — ongoing improvements, merged into main after review.

Each branch has its own deployed Streamlit app, so ongoing work never affects the version under review. Once an assignment is approved, `dev` is merged into `main`.

## Data source

Weekly reservoir statistics from NVE's [magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/om-magasinstatistikken/) dataset.