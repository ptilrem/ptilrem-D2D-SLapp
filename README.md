# ptilrem-D2D-SLapp

- Version: 2.0
- Author: ptilrem

# Assignment Dashboard

A Streamlit dashboard exploring Norwegian hydropower reservoir statistics and cross-border electricity transfers. This is part of a four-part university project in which each assignment builds on the previous one.

In Assignment 1, the app read reservoir statistics from a local CSV file. In Assignment 2, reservoir data comes directly from the NVE Magasinstatistikk API, and a new page displays electricity-transfer data stored in MongoDB Atlas.

## Links

- **GitHub repository:** https://github.com/ptilrem/ptilrem-D2D-SLapp
- **Live app:** https://ptilrem-d2d-slapp.streamlit.app/
- **Assignment 1 notebook:** notebook/assignment1.ipynb / notebook/assignment1.pdf
- **Assignment 2 notebook:** notebook/assignment2.ipynb (rename or update this path to match the submitted file)

## Project structure

```
├── data/
│   └── reservoirs.csv          # Raw weekly reservoir data from NVE
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

## Running locally

```bash
git clone https://github.com/ptilrem/ptilrem-D2D-SLapp.git
cd ptilrem-D2D-SLapp
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run streamlit_app/Home.py
```

## Branching workflow

- `main` — holds the latest **approved** hand-in.
- `dev` — active working branch for the current assignment.

Each branch has its own deployed Streamlit app, so ongoing work never affects the version under review. Once an assignment is approved, `dev` is merged into `main`.

## Data source

Weekly reservoir statistics from NVE's [magasinstatistikk](https://www.nve.no/energi/analyser-og-statistikk/om-magasinstatistikken/) dataset.