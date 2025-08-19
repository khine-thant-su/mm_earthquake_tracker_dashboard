import calendar
import streamlit as st
import altair as alt
import pandas as pd
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
from zoneinfo import ZoneInfo
from map_quakes import get_quake_data

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
df = get_quake_data()  # returns a pandas DataFrame

####################### Show line plot #######################
# Change to datetime format to extract month
df['date'] = pd.to_datetime(df['timestamp'])  # Returns a Series where each element is a timestamp
df['month'] = df['date'].dt.month  # df['month'] is a Series

# Make a dataframe with monthly quake counts
monthly_counts = df.groupby('month').size()  # Count the number of quakes in each month
monthly_quakes_df = pd.DataFrame(data={'month':monthly_counts.index, 'monthly_quakes':monthly_counts})

# Change month names from number to letter
monthly_quakes_df['month_name'] = monthly_quakes_df['month'].apply(lambda x: calendar.month_abbr[x])

# To make Altair line chart display month names in calendar order, convert the 'month_name' column to a categorical type with an explicit order.
month_order = [m for m in calendar.month_abbr]  # Extract month names
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

st.markdown("##### Monthly earthquake counts")
st.altair_chart(chart, use_container_width = True) # Match the width of the parent container

####################### Show map #######################
map_center = [21.5, 96.0]   # Center map on Myanmar
mm_tzone = ZoneInfo("Asia/Yangon")

# Create a base map
m = folium.Map(location=map_center, zoom_start=5, tiles='CartoDB positron')

for _, row in df.iterrows():
    folium.CircleMarker(
        location = [row['latitude'], row['longitude']],
        radius = row['magnitude'] ** 1.5,  # scale radius by magnitude
        popup = f"Magnitude: {row['magnitude']}<br>Depth: {row['depth']}<br>Time: {row['timestamp'].astimezone(mm_tzone)}",
        color = 'green' if row['magnitude'] <= 3.9 else 'orange' if row['magnitude'] <= 5.9 else 'red',  # Earthquake magnitude classifications from University of Alaska Fairbanks Earthquake Center
        fill = True,
        fill_opacity = 0.5
    ).add_to(m)

# Define the legend's HTML using Branca
# 'this' refers to the current Folium map object, 'kwargs' is a dict of keyword arguments passed to the macro.
legend_html = """
{% macro html(this, kwargs) %}  
<div style="
    position: fixed; 
    bottom: 40px; left: 30px; width: 170px; height: 130px; 
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
    Bigger circles = higher magnitude 
</div>
{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)

# Add the legend to the map
m.get_root().add_child(legend)

st.markdown("##### Location of earthquakes")
st_folium(m, width=700, height=500)