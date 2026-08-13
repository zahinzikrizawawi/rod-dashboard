# Rapid On-Demand Fleet Analysis Dashboard

An interactive Streamlit dashboard for analyzing Rapid On-Demand's ride operations —
demand patterns, spatial hotspots, OD (Origin-Destination) flows, fleet allocation,
and zone-level service performance.

## Pages

1. **Executive Summary** — high-level KPIs, daily demand trends, top zones
2. **Spatial Demand Analysis** — interactive pickup/dropoff heat map by zone and stop
3. **OD Strategic Flow Analysis** — dominant OD pairs and flow maps for fleet staging
4. **Fleet Allocation Analysis** — van deployment vs. demand across zones and hours
5. **Zone Performance Analysis** — waiting/travel/total time performance by zone

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/rod-dashboard.git
cd rod-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your dataset
Place your trip data CSV at:
```
data/rod_clean_daily_order_with_coordinates.csv
```
(A small sample file is included so the app runs out of the box.)

### 4. Run the app
```bash
streamlit run Home.py
```

The app will open at `http://localhost:8501`. Use the sidebar to navigate between pages.

## Project Structure
```
rod_dashboard/
├── Home.py                          # Main entry point / landing page
├── utils.py                         # Shared data loader + styling
├── requirements.txt
├── data/
│   └── rod_clean_daily_order_with_coordinates.csv
└── pages/
    ├── 1_Executive_Summary.py
    ├── 2_Spatial_Demand_Analysis.py
    ├── 3_OD_Flow_Analysis.py
    ├── 4_Fleet_Allocation_Analysis.py
    └── 5_Zone_Performance_Analysis.py
```

## Tech Stack
- [Streamlit](https://streamlit.io/) — app framework
- [Pandas](https://pandas.pydata.org/) — data processing
- [Plotly](https://plotly.com/python/) — interactive charts and maps
