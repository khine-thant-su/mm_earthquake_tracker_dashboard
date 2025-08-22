from map_quakes import get_quake_data
import pandas as pd
import calendar   # To get month names
import streamlit as st
import streamlit.components.v1 as components  # To render the html map with a custom legend
import altair as alt   # To make line plot
import folium   # To make map
from branca.element import Element   # To insert custom legend to Folium map
from zoneinfo import ZoneInfo   # To change display to Myanmar Time Zone

st.title("2025 Earthquakes in Myanmar")
# components.html(
#     "<p><span style='text-decoration: line-through double red;'>Oops</span>!</p>"
# )

st.set_page_config(
    page_title="Myanmar Earthquakes Dashboard",
    page_icon="⛑️",
    layout= "centered"
)

# Get data from DB
df = get_quake_data()  # Returns a pandas DataFrame

####################### Show line plot #######################
st.markdown("##### Monthly earthquake counts")

# Change to datetime format to extract month
df['date'] = pd.to_datetime(df['timestamp'])  # Returns a Series where each element is a timestamp
df['month'] = df['date'].dt.month  # df['month'] is a Series

# Make a dataframe with monthly quake counts
monthly_counts = df.groupby('month').size()  # Count the number of quakes in each month
monthly_quakes_df = pd.DataFrame(data={'month':monthly_counts.index, 'monthly_quakes':monthly_counts})

# Change month names from number to letter
monthly_quakes_df['month_name'] = monthly_quakes_df['month'].apply(lambda x: calendar.month_abbr[x])

month_order = [m for m in calendar.month_abbr]  # Extract month names

# To make Altair line chart display month names in calendar order, convert the 'month_name' column to a categorical type with an explicit order.
monthly_quakes_df['month_name'] = pd.Categorical(
    monthly_quakes_df['month_name'],
    categories = month_order,
    ordered = True)

# Create line chart
line = alt.Chart(monthly_quakes_df).mark_line().encode(
        alt.X('month_name:N', title='Month', sort = month_order, axis=alt.Axis(tickMinStep=1, labelAngle=0)),  # N means nominal
        alt.Y('monthly_quakes:Q').title('Number of earthquakes'),
    )

points = alt.Chart(monthly_quakes_df).mark_circle(size = 50, filled = True, color = 'red').encode(
    alt.X('month_name:N', sort = month_order),
    alt.Y('monthly_quakes:Q'),
    tooltip = [
        alt.Tooltip('month_name:N', title = 'Month'),
        alt.Tooltip('monthly_quakes:Q', title = 'Num of earthquakes')] # The information that appears when a user hovers over a data point in the chart
)

chart = line + points

st.altair_chart(chart, use_container_width = True) # Match the width of the parent container

####################### Show map with month filter #######################
st.markdown("##### Location of earthquakes")

### Month filter

available_months = sorted(df['timestamp'].dt.month.unique())
month_options = ["All quakes"] + [calendar.month_name[m] for m in available_months]  # Convert numeric to text month names

# Month selection widget
selected_month_name = st.selectbox("Select a month to filter earthquakes", month_options, index = 0, width = 300)  # Default to "All quakes" option

# Filter data based on month selection
filtered_df = (
    df if selected_month_name == "All quakes"
    else df[df['timestamp'].dt.month == list(calendar.month_name).index(selected_month_name)]
)

### Build map

map_center = [21.5, 96.0]  # Center map on Myanmar
mm_tzone = ZoneInfo("Asia/Yangon")

def make_map(location, timezone, data):
    """Makes a Folium map that shows magnitude, depth, and time for each earthquake, and a magnitude legend."""

    # Create a base map
    m = folium.Map(location=location, zoom_start=5, tiles='CartoDB positron')

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            popup=f"Magnitude: {row['magnitude']}<br>Depth: {row['depth']}<br>Time: {row['timestamp'].astimezone(timezone)}",  # Convert to local timezone to be displayed on map
            color='green' if row['magnitude'] <= 3.9 else 'orange' if row['magnitude'] <= 5.9 else 'red',  # Earthquake magnitude classifications from University of Alaska Fairbanks Earthquake Center
            fill=True,
            fill_opacity=0.5
        ).add_to(m)

    # Add a custom HTML legend to the Folium map
    legend_html = """
    <div style="
        position: fixed;
        bottom: 40px; left: 30px; width: 170px; height: 100px;
        background-color: white;
        border: 2px solid grey;
        z-index: 9999;
        font-size: 12px;
        padding: 8px;
    ">
        <b>Magnitude Legend</b><br>
        <i style="color:green;">●</i> Minor (≤ 3.9)<br>
        <i style="color:orange;">●</i> Moderate (4.0–5.9)<br>
        <i style="color:red;">●</i> Strong (≥ 6.0)<br>
    </div>
    """
    # Add the legend to the map
    m.get_root().html.add_child(Element(legend_html))

    return m

m = make_map(map_center, mm_tzone, filtered_df)

# Save the map to an HTML file
m.save("quake_map_with_legend.html")

# Read the HTML file
with open("quake_map_with_legend.html", "r", encoding = "utf-8") as file:
    html_content = file.read()

# Render html map inside Streamlit app
components.html(html_content, height = 500)




