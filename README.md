# Earthquake Data Dashboard for Myanmar

This repository contains Python scripts that scrape, clean, store, and visualize earthquake data from the USGS (United States Geological Survey) API, with a focus on earthquakes in Myanmar.

## 📌 Features

- Scrapes earthquake data from the USGS API within a specified date range and geographic bounding box.
- Filters and cleans the data to retain only earthquakes relevant to Myanmar.
- Stores the cleaned data in a PostgreSQL database.
- Visualizes earthquake locations on an interactive map using Folium.

## 🗂️ Project Structure

- `scrape&cleandata.py`: Fetches, parses, and cleans earthquake data from Myanmar using the USGS API. Inserts cleaned earthquake data into a PostgreSQL database.
- `map_quakes.py`: Generates an interactive map of earthquakes using Folium.
- `config.py`: Contains configuration settings such as database name, user, password, host, and port.
- `db_connection.py`: Manages the PostgreSQL database connection.
- `README.txt`: This file.

## 🧪 Usage Instructions

1. Configure the database connection
Edit config.py to include your PostgreSQL credentials (e.g., dbname, user, password, host, port).

2. Fetch and parse earthquake data
Run scrape&cleandata.py to retrieve raw earthquake data from the USGS API, clean the data, and insert cleaned data to the PostgreSQL database.

3. Visualize the data
Run map_quakes.py to generate an interactive map of the earthquakes using Folium.
