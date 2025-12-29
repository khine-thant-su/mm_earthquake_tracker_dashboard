from sqlalchemy import create_engine  # To establish connection to a SQL database
import pandas as pd
import calendar   # To get month names
import streamlit as st
import streamlit.components.v1 as components  # To render the html map with a custom legend
import altair as alt   # To make line plot
import folium   # To make map
from branca.element import Element   # To insert custom legend to Folium map
from zoneinfo import ZoneInfo   # To change display to Myanmar Time Zone

@st.cache_data(ttl="7d")
# Get data from DB
def fetch_data():
    conn_info = st.secrets["connections"]["neon"]
    engine = create_engine(
        f"{conn_info['dialect']}+psycopg2://{conn_info['username']}:{conn_info['password']}@{conn_info['host']}:{conn_info['port']}/{conn_info['database']}"
    )
    return pd.read_sql("SELECT * FROM quake_info;", engine)

df = fetch_data()

# Note: if you don't use st.cache_data decorator and call df directly, pd.read_sql() line will be run every time the dashboard loads/refreshes due to user interaction. This eats up your database's compute hours.

st.set_page_config(
    page_title="Myanmar Earthquakes Dashboard",
    page_icon="⛑️",
    layout= "centered"
)

st.image("pictures/earthquake_photo_main.jpeg", caption = "Collapsed buildings in Myanmar following the 7.7 magnitude earthquake in March 2025. \nSource: [Amnesty International](https://www.amnesty.org/en/latest/news/2025/04/myanmar-inhumane-military-attacks-in-earthquake-areas-hindering-relief-efforts/)")

st.title("2025 Earthquakes in Myanmar")
st.info("""In **March 2025**, a powerful **7.7-magnitude earthquake** struck Myanmar's Sagaing Region, marking one of the country's deadliest natural disasters in recent history. Over **5,000 people** died, and many more were displaced.

- Ongoing military assault of civilians in Myanmar severely hindered relief efforts and accurate reporting of the earthquake's death toll.
- Despite fading global attention, **seismic activity continues** across Myanmar.
- This app monitors earthquakes in Myanmar since **January 2025** to raise awareness of the ongoing threat to lives and livelihoods.
""", icon="🚨")

st.divider()

st.info(f""" #### Key takeaways  
- Since January 2025, **{len(df)} earthquakes** have been recorded in Myanmar.  
- **68 earthquakes** happened after the catastrophic March event.
- **9 were magnitude 5 or higher**, posing serious risks.
- Seismic activity remains concentrated in **central Myanmar**, near the **Sagaing Region**, the epicenter of the March quake. 
- This pattern suggests **continued earthquake danger** and ongoing **threat to lives** in the region.
""")


st.image("pictures/earthquake_photo_2.png", caption = "A collapsed building in Mandalay, Myanmar -- about 11 miles (17.2 km) from the epicenter of the 7.7 magnitude earthquake in March 2025. Source: [The Guardian](https://www.theguardian.com/world/gallery/2025/mar/29/our-town-looks-like-a-collapsed-city-myanmar-earthquake-in-pictures)")

st.divider()
####################### Show line plot #######################
st.markdown("#### Number of earthquakes per month (Jan 2025 - present)")

# Change to datetime format to extract month
df['month'] = df['timestamp'].dt.month

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
        alt.X('month_name:N', title='Month', sort = month_order, axis=alt.Axis(tickMinStep=1, labelAngle=0)),  # N means nominal data (categorical and unordered). Tells Altair to treat month names as discrete categories.
        alt.Y('monthly_quakes:Q').title('Number of earthquakes'),  # Q means quantitative data
    )

# Add vertical line for March 2025
march_line = alt.Chart(pd.DataFrame({
    'month_name': ['Mar'],
    'label': ["March 2025: Major Earthquake"]
})).mark_rule(color = "red").encode(
    x = alt.X('month_name:N', sort = month_order),
    tooltip = 'label:N'
)

# Add label above the line
march_text = alt.Chart(pd.DataFrame({
    'month_name': ['Mar'],
    'monthly_quakes': [monthly_quakes_df['monthly_quakes'].max()],  # place label at top
    'label': ["March 2025: Major Earthquake"]
})).mark_text(dy=-10, color='red').encode(
    x = alt.X('month_name:N', sort = month_order),
    y = 'monthly_quakes:Q',
    text='label:N'
)

points = alt.Chart(monthly_quakes_df).mark_circle(size = 50, filled = True, color = 'red').encode(
    alt.X('month_name:N', sort = month_order),
    alt.Y('monthly_quakes:Q'),
    tooltip = [
        alt.Tooltip('month_name:N', title = 'Month'),
        alt.Tooltip('monthly_quakes:Q', title = 'Num of earthquakes')] # The information that appears when a user hovers over a data point in the chart
)

chart = line + march_line + march_text+ points

st.altair_chart(chart, use_container_width = True) # Match the width of the parent container

st.info("""Since the major earthquake in March, seismic activities have continued at a higher rate per month than before. This suggests continued earthquake danger in Myanmar.
""")

st.divider()
####################### Magnitude histogram #######################
st.markdown("#### Earthquake magnitude distribution (Jan 2025 - present)")

hist = alt.Chart(df).mark_bar().encode(
    alt.X("magnitude:Q", bin=alt.Bin(step=0.5), title="Magnitude"),
    alt.Y("count():Q", title="Frequency"),
    tooltip=[alt.Tooltip("count():Q", title="Frequency")]
).properties(
    width=600,
    height=400
)

# Display the histogram
st.altair_chart(hist, use_container_width=True)

st.markdown("""**Note**: Each bin includes values ≥ left edge and < right edge.  
For e.g. 4.0-4.5 bin includes earthquakes with 4.0 magnitude but not those with 4.5 magnitude.  """)

st.info("""Most earthquakes have been in the minor-light range (3.0-4.9 magnitude).  
But there have been **9 earthquakes** since March that were in moderate-major range (5.0-7.9 magnitude).
""")

st.divider()

####################### Show map with month filter #######################
st.markdown("#### Location of earthquakes (Jan 2025 - present)")

### Month filter

available_months = sorted(df['timestamp'].dt.month.unique())
month_options = ["All quakes"] + [calendar.month_name[m] for m in available_months]  # Convert numeric to text month names

# Month selection widget
selected_month_name = st.selectbox("Select a month to filter earthquakes", month_options, index = 0, width = 300)  # Default to "All quakes" option
st.markdown("**Click on a circle to see the magnitude, depth, and time of each earthquake.**")

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

# Render HTML map inside Streamlit app
components.html(html_content, height = 500)

st.divider()

st.image("pictures/earthquake_photo_3.jpg", caption = "Residents of Sagaing Township, the epicenter of the earthquake, have been spending their days and nights outdoors since March 28. Source: [Democratic Voice of Burma](https://english.dvb.no/earthquake-epicenter-of-sagaing-region-two-months-later/)")

####################### Donation resources #######################
st.header("""What can you do to help?""")

st.info("""
If you are able, please consider donating to community-led earthquake relief efforts in Myanmar.  

Below you will find trustworthy organizations working with grassroots responders -- **not through the Myanmar military-controlled channels** -- to provide earthquake relief to impacted communities.
""")

card_height = 400

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.image("pictures/better_burma_logo.png", width=160)
        st.markdown("##### [Better Burma](https://www.betterburma.org)")
        st.write("A U.S.-based non-profit supporting Myanmar people through humanitarian aid and advocacy")
        st.link_button("Donate", "https://www.betterburma.org/earthquakerelief")

with col2:
    with st.container():
        st.write("\n" * 8)  # Spacer to align image with col1
        st.image("pictures/mutual_aid_myanmar_logo.png", width=200)
        st.write("\n" * 2)
        st.markdown("##### [Mutual Aid Myanmar](https://www.mutualaidmyanmar.org/)")
        st.write("A collection of activists, academics, and policy makers supporting the democracy movement in Myanmar")
        st.link_button("Donate", "https://www.mutualaidmyanmar.org/earthquake")

with col3:
    with st.container():
        st.write("\n" * 6)  # Spacer to align image with col1 & col2
        st.image("pictures/us_campaign_burma_logo.png", width=190)
        st.markdown("##### [U.S. Campaign for Burma](https://www.uscampaignforburma.org/)")
        st.write("An organization of Burmese and Americans promoting human rights in Myanmar")
        st.link_button("Donate", "https://actionnetwork.org/fundraising/us-campaign-for-burma-donation-page/")
