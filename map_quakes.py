# This script reads quake data from the PostgreSQL database, and creates an interactive map using Folium, where each earthquake is marked with a popup showing location, magnitude, depth, and time.


import folium
import pandas as pd
from sqlalchemy import create_engine
from config import DB_CONFIG
from folium.plugins import MarkerCluster
from zoneinfo import ZoneInfo


def get_quake_data():
    """Fetch earthquake data from PostgreSQL.
    :returns a Dataframe."""
    # Create the SQLAlchemy engine using PG8000 as the driver
    engine = create_engine(
        f"postgresql+pg8000://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:5432/{DB_CONFIG['dbname']}")

    df = pd.read_sql("quake_info", engine)
    return df

def create_folium_map(quake_df):
    """Create a folium map with earthquake markers. Timezone shows Myanmar time.
    :returns a map."""
    map_center = [21.5, 96.0]   # Center map on Myanmar
    quake_map = folium.Map(location=map_center, zoom_start=6, tiles='CartoDB positron')
    mm_tzone = ZoneInfo("Asia/Yangon")  # Myanmar time zone

    # Cluster the markers
    marker_cluster = MarkerCluster().add_to(quake_map)

    for _, row in quake_df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        mag = row['magnitude']
        place = row['place']
        # time = row['timestamp'].strftime("%Y-%m-%d %H:%M")
        time_mmt = row['timestamp'].astimezone(mm_tzone)
        time_str = time_mmt.strftime("%Y-%m-%d %H:%M %Z")
        depth = row['depth']

        popup_html = f"""
            <b>Location:</b> {place}<br>
            <b>Magnitude:</b> {mag}<br>
            <b>Depth:</b> {depth} km<br>
            <b>Time:</b> {time_str}
            """

        # Color scale: green (low mag) → red (high mag)
        color = 'green' if mag < 3 else 'orange' if mag < 5 else 'red'
        radius = 3 + mag ** 1.5  # scale radius by magnitude

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(marker_cluster)

    return quake_map


def main():
    print("🌍 Loading quake data...")
    quake_df = get_quake_data()
    print(f"{len(quake_df)} earthquake records loaded.")

    print("🗺️ Creating map...")
    fmap = create_folium_map(quake_df)

    output_file = "myanmar_quakes_map.html"
    fmap.save(output_file)
    print(f"✅ Map saved to {output_file}")


if __name__ == "__main__":
    main()