import streamlit as st
import osmnx as ox
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Function to generate map
def display_map(city_name):
    st.subheader(f"Map of {city_name}")

    try:
        # Fetch urban boundary
        boundary = ox.geocode_to_gdf(city_name)

        # Fetch green areas
        green_tags = {
            "leisure": ["park", "garden"],
            "landuse": ["grass", "meadow"],
            "natural": ["wood", "grassland"]
        }
        green_areas = ox.features_from_place(city_name, tags=green_tags)

        # Create folium map
        centroid = boundary.geometry.centroid.iloc[0]
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)

        # Add layers
        folium.GeoJson(boundary, name="Urban Boundary", style_function=lambda x: {"color": "blue"}).add_to(m)
        folium.GeoJson(green_areas, name="Green Areas", style_function=lambda x: {"color": "green"}).add_to(m)

        # Display map
        folium_static(m)

    except Exception as e:
        st.error(f"Error fetching map data: {e}")

# Streamlit UI
st.title("Urban Eco Tool 🌍")
st.write("Analyze urban areas and optimize green spaces.")

# User input for city name
city_name = st.text_input("Enter a city name:", "Mysuru, India")

# Button to generate the map
if st.button("Show Map"):
    display_map(city_name)

