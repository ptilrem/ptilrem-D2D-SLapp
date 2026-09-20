# ptilrem-D2D-SLapp

- Version: 1.0
- Author: ptilrem

# Assignment Dashboard

A Streamlit dashboard exploring weekly Norwegian reservoir fill data from NVE (Norges vassdrags- og energidirektorat). Built as part of a semester-long, four-part assignment, where each part builds on the last.

## Links

- **Live app:** https://ptilrem-d2d-slapp.streamlit.app/
- **Notebook (PDF):** see `notebook/assignment1.pdf`

## Project structure

```
├── data/
│   └── reservoirs.csv          # Raw weekly reservoir data from NVE
├── notebook/
│   └── assignment1.ipynb       # Data exploration, cleaning, and plotting (Assignment 1 lab work)
├── streamlit_app/
│   ├── Home.py                 # Sets up page config and navigation
│   ├── pages/
│   │   ├── home_content.py     # Home page content
│   │   ├── data_table.py       # Data table view with LineChartColumn trends
│   │   ├── data_plot.py        # Interactive plot with column/date-range filters
│   │   └── about.py            # Project background, data source, and links etc.
│   ├── utils/
│   │   └── data.py             # DataLoader class: reads, renames, and prepares the data
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