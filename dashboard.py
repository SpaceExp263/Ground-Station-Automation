"""
Satellite Dashboard Development Plan and Resources
1. Page 1. Satellite Data Analysis
    a. Launch site Density: Which country satellite and launched from where::::  Scatter Plots on Mapbox in Python
    b. Orbital Density (LEO/GEO/SUN SYNCHRONOUS)
    c. Object type distribution: Payload/Rocket body/Debris
    d. Launch trends over time
    Data to be taken from the SATCAT excel file
    Origin: Space Track

2. Page 2. Customised Ground Station Information
    a. Norad CAT ID: Input
    b. CDM table and Embed orbit visualizer using cesiumjs and visualize the orbit of the object and what it is about to collide
    (https://daoneil.github.io/spacemission/Apps/20160411_Visualization_of_OrbitalDebris_with_Cesium_and_Satellitejs_Tutorial.pdf)
    c. Current TLE and Decay Info

Columns of the excel sheet

Index(['INTLDES', 'NORAD_CAT_ID', 'OBJECT_TYPE', 'SATNAME', 'COUNTRY',
       'LAUNCH', 'SITE', 'DECAY', 'PERIOD', 'INCLINATION', 'APOGEE', 'PERIGEE',
       'COMMENT', 'COMMENTCODE', 'RCSVALUE', 'RCS_SIZE', 'FILE', 'LAUNCH_YEAR',
       'LAUNCH_NUM', 'LAUNCH_PIECE', 'CURRENT', 'OBJECT_NAME', 'OBJECT_ID',
       'OBJECT_NUMBER'],
      dtype='object')

"""
import pandas as pd
from spacetrack import SpaceTrackClient
import streamlit as st
import plotly.express as px


#st = SpaceTrackClient(identity='palak002@e.ntu.edu.sg', password='PalakPorwalrocks15')
df = pd.read_excel(r"C:\Users\Palak002\Downloads\SATCAT.xlsx",sheet_name="Sheet1")

# Set the page config to wide mode with a specific title
st.set_page_config(layout="wide", page_title="Satellite Data Analysis", initial_sidebar_state="auto")

# Create three columns
launch=df["COUNTRY"].value_counts().head(20)
with st.sidebar:
    st.write("Index")

# Assuming 'df' is your DataFrame and you've already grouped by 'LAUNCH_YEAR' and 'COUNTRY' to get 'NUMBER_OF_LAUNCHES'
launches_per_country_year = df.groupby(['LAUNCH_YEAR', 'COUNTRY']).size().reset_index(name='NUMBER_OF_LAUNCHES')
total_launches_per_country = launches_per_country_year.groupby('COUNTRY')['NUMBER_OF_LAUNCHES'].sum().reset_index()
top_10_countries = total_launches_per_country.sort_values(by='NUMBER_OF_LAUNCHES', ascending=False).head(10)['COUNTRY']
top_launches_per_country_year = launches_per_country_year[launches_per_country_year['COUNTRY'].isin(top_10_countries)]
fig = px.scatter(top_launches_per_country_year, x="LAUNCH_YEAR", y="NUMBER_OF_LAUNCHES",
                 color="COUNTRY",  # Use color to distinguish between countries.
                 size="NUMBER_OF_LAUNCHES",  # Use size to represent the number of launches.
                 hover_name="COUNTRY",  # Show country name on hover.
                 animation_frame="COUNTRY",  # Animate by country.
                 #animation_group="COUNTRY",  # Ensure each country is treated as a distinct entity.
                 range_y=[0, 1000],  # Optional: adjust based on your data's range.
                 size_max=150  # Significantly larger bubbles
                 )
fig["layout"].pop("updatemenus")

st.caption("Launch trend for each country per year")
st.plotly_chart(fig, use_container_width=True)

# Bottom section: Orbital Density and Object Type Distribution
st.write("---")  # Adding a visual separator

def classify_orbit(orbital_period_minutes):
    if orbital_period_minutes <= 120:
        return 'Low Earth Orbit (LEO)'
    elif 120 < orbital_period_minutes <= 720:
        return 'Medium Earth Orbit (MEO)'
    elif abs(orbital_period_minutes - 1436) <= 10:  # Allowing some margin around 24 hours
        return 'Geostationary Orbit (GEO)'
    else:
        return 'Highly Elliptical Orbit (HEO)'

# Assuming your DataFrame is named df and has a column 'PERIOD' with orbital period in minutes
df['ORBIT_TYPE'] = df['PERIOD'].apply(classify_orbit)

col3, col4 = st.columns(2)

with col3:
    st.caption('Orbital Density')

    # Calculate the counts for each orbit type
    orbit_counts = df['ORBIT_TYPE'].value_counts()

    # Streamlit's columns for layout
    col3a, col3b, col3c, col3d = st.columns(4)

    # Using the columns to display each orbit type's count
    with col3a:
        st.metric(label="LEO", value=orbit_counts.get('Low Earth Orbit (LEO)', 0))
    with col3b:
        st.metric(label="MEO", value=orbit_counts.get('Medium Earth Orbit (MEO)', 0))
    with col3c:
        st.metric(label="GEO", value=orbit_counts.get('Geostationary Orbit (GEO)', 0))
    with col3d:
        st.metric(label="HEO", value=orbit_counts.get('Highly Elliptical Orbit (HEO)', 0))


with col4:
    st.caption('Object Type Distribution')
    # Prepare the data for the Sunburst chart
    object_type_df = df['OBJECT_TYPE'].value_counts().reset_index()
    object_type_df.columns = ['Object Type', 'Count']

    # Creating a Sunburst chart
    object_type_fig = px.sunburst(object_type_df,
                                  path=['Object Type'],
                                  values='Count',
                                  color='Count',
                                  color_continuous_scale='Agsunset')
    st.plotly_chart(object_type_fig, use_container_width=True)
