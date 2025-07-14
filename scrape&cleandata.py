import requests
import pandas as pd
from datetime import datetime, timezone
from db_connection import get_db_connection

### Scrape information from USGS
# Define Myanmar bounding box (approximate)
MYANMAR_BOUNDS = {
    "minlatitude": 10, # Change to 15 if we want Yangon Region as the southernmost point
    "maxlatitude": 28.5,
    "minlongitude": 92,
    "maxlongitude": 99
}

def fetch_earthquake_data(start_date:str, end_date:str, min_magnitude: float = 2.5):
    """Fetch earthquake data from the USGS API.
    :returns a dict resulting from parsing the JSON content of the API response.
    """
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": end_date,
        **MYANMAR_BOUNDS,
        "minmagnitude": min_magnitude,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def parse_earthquake_data(data):
    """Extract relevant features from the raw USGS GeoJSON response.
    :returns a Dataframe with quake info."""
    features = data.get("features", [])
    quake_list = []

    for feature in features:
        timestamp = feature['properties']['time']
        magnitude = feature['properties']['mag']
        place = feature['properties']['place']
        coords = feature['geometry']['coordinates']
        longitude, latitude = coords[0], coords[1]
        depth = coords[2] if len(coords) > 2 else None

        quake_list.append({
            "timestamp": datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc),  # convert from milliseconds to seconds and to UTC datetime
            # If tz=None, timestamp will be converted to the platform's local date and time. The returned datetime object is naive.
            "magnitude": magnitude,
            "longitude": longitude,
            "latitude": latitude,
            "depth": depth,
            "place": place
        })

    return pd.DataFrame(quake_list)

def clean_earthquake_data(df):
    """Keep only earthquakes within Burma/Myanmar."""
    original_len = len(df)
    df = df[df["place"].str.contains("Burma|Myanmar", na=False)]
    removed = original_len - len(df)
    print(f"{removed} rows removed because they weren't in Burma/Myanmar.")
    return df


def save_quake_data(conn, timestamp, magnitude, longitude, latitude, depth, place):
    """Insert a single earthquake record into PostgresSQL."""
    try:
        with conn.cursor() as cur:
            # Check if entry with the same timestamp and place already exists
            cur.execute("""
            SELECT timestamp, place
            FROM quake_info
            WHERE timestamp = %s
            """, (timestamp,))
            result = cur.fetchone()  # Fetch one row from the results
            # If there’s no existing quake with that timestamp, `result` will be `None`.

            if result:
                existing_timestamp, existing_place = result
                if (existing_timestamp == timestamp and
                existing_place == place):
                    print("The scraped data already exists in the quake_info table in the database.")
                    return

            # If not the same (or no row exists), insert the new data
            cur.execute("""
                INSERT INTO quake_info (timestamp, magnitude, longitude, latitude, depth, place)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (timestamp, magnitude, longitude, latitude, depth, place))

            conn.commit()  # Commit the transaction


    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to process {timestamp, place}: {e}")

def main():
    start_date = "2025-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    print("Fetching earthquake data...")
    raw_data = fetch_earthquake_data(start_date, end_date)
    parsed_df = parse_earthquake_data(raw_data)

    print("Cleaning data...")
    clean_df = clean_earthquake_data(parsed_df)

    print("Saving data to PostgresSQL...")
    conn = get_db_connection()
    for _, row in clean_df.iterrows():  # "_" is the row's index, "row" is a Series object containing each row's data.
        try:
            save_quake_data(
                conn,
                row['timestamp'],
                row['magnitude'],
                row['longitude'],
                row['latitude'],
                row['depth'],
                row['place']
            )
        except Exception as e:
            print(f"Failed to save data to Postgres database: {e}")

    conn.close()
    print(f"✅ Saved quake data from {start_date} to {end_date} in the Postgres database.")

if __name__ == "__main__":
    main()


# Check the data stored in Postgres database
# conn = get_db_connection()
# with conn.cursor() as cur:
#     cur.execute("""
#             SELECT *
#             FROM quake_info
#             ORDER BY timestamp desc
#             LIMIT 1
#             """,)
#     result = cur.fetchall()
#
# print(result)

# conn = get_db_connection()
# with conn.cursor() as cur:
#     cur.execute("SELECT MAX(timestamp) FROM quake_info;")
#     result = cur.fetchone()
# print(result)

