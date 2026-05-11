[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Momahmoses%2Fng-traffic-congestion-lagos&branch=main&mainModule=app.py)

# 🚦 Lagos Traffic Congestion Analytics

Real-time traffic congestion monitoring for Lagos — Africa's largest city — using GPS probe data, **PySpark Stream Processing**, **GIS heatmaps**, **Azure Stream Analytics**, and a **Streamlit** live dashboard.

## Problem Statement
Lagos loses an estimated **$1 billion annually** to gridlock. Corridors like Third Mainland Bridge, Apapa-Oshodi, and Lekki-Epe Expressway routinely see speeds below 10 km/h during peak hours. This platform helps LASTMA, urban planners, and ride-hailing operators make data-driven traffic management decisions.

## Tech Stack
| Layer | Technology |
|---|---|
| Geospatial | GeoPandas, Folium HeatMap, Shapely |
| Big Data | PySpark on Azure Databricks |
| Cloud | Azure Stream Analytics, Azure Event Hubs, Azure Maps |
| Dashboard | Streamlit + Plotly |

## Project Structure
```
ng-traffic-congestion-lagos/
├── app.py
├── pipeline/spark_pipeline.py    # Congestion index + travel time model
├── gis/spatial_analysis.py       # Corridor heatmap + incident clustering
├── data/generate_data.py         # Synthetic GPS probes + incidents
├── azure/azure_config.py         # Stream Analytics + Event Hubs config
└── requirements.txt
```

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dashboard Features
- Live congestion heatmap (dark map, color-coded by severity)
- Speed by corridor horizontal bar chart
- Hourly congestion area chart with AM/PM peak markers
- Incident type pie chart
- Worst corridors ranking table

## Data Sources (Production)
- **HERE Maps / Google Maps Traffic API** — GPS probe feeds
- **LASTMA** — Lagos State Traffic Management Authority incidents
- **OpenStreetMap** — Road network
- **Azure Event Hubs** — Real-time GPS device ingestion
