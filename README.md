[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://myanmar-earthquakes.streamlit.app/)

# Earthquake Data Dashboard for Myanmar

This repository contains Python scripts that scrape, clean, store, and visualize earthquake data from the [United States Geological Survey (USGS) API](https://earthquake.usgs.gov/fdsnws/event/1/) for earthquakes, with a focus on earthquakes in Myanmar. <br>

The Streamlit app visualizes earthquake data and allows users to explore seismic activity interactively. 

## 📌 Features

- Scrapes earthquake data from the USGS API within a specified date range and geographic bounding box specifying Myanmar.
- Interactive map showing earthquakes filterable by month

## ⚡ Technical highlights

- **Streamlit**: Provides the frontend UI and interactive components for the app.
- **Neon (PostgreSQL)**: A serverless cloud database that stores earthquake data, used for deployment.
- **SQLAlchemy & psycopg2-binary**: Used to connect to the Neon database and fetch data into Pandas DataFrames.
- **Pandas**: For data manipulation and preprocessing before visualization.
- **Folium / Altair**: Used for map visualization and plotting interactive charts.
- **Secrets management**: `.streamlit/secrets.toml` (locally) and Streamlit Cloud secrets are used to securely store database credentials.
- **Deployment**: Hosted on Streamlit Cloud.

## 🗂️ Project structure

- `scrape&cleandata.py`: Fetches, parses, and cleans earthquake data from Myanmar using the USGS API. Inserts cleaned earthquake data into a PostgreSQL database.
- `streamlit_app.py`: Builds the Streamlit app that shows earthquakes over time and on a map.
- `db_connection.py`: Manages the local PostgreSQL database connection.
- `README.md`: This file.

## 🧪 Usage Instructions

1. Clone the repo
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `streamlit run streamlit_app.py`

**NOTE:** Earthquake magnitude classification referenced from [Alaska Earthquake Center.](https://earthquake.alaska.edu/earthquake-magnitude-classes)
