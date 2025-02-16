import streamlit as st
import osmnx as ox
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Set Nominatim endpoint and user-agent to avoid connection issues
ox.settings.nominatim_endpoint = "https://nominatim.openstreetmap.de"


def fetch_urban_data(city_name):
    """Fetch urban boundary and green areas for a city."""
    boundary = ox.geocode_to_gdf(city_name)
    green_tags = {
        "leisure": ["park", "garden"],
        "landuse": ["grass", "meadow"],
        "natural": ["wood", "grassland"]
    }
    green_areas = ox.features_from_place(city_name, tags=green_tags)
    return boundary, green_areas

def display_map(city_name):
    """Display an interactive map with urban boundary and green areas."""
    boundary, green_areas = fetch_urban_data(city_name)
    m = folium.Map(location=[boundary.centroid.y[0], boundary.centroid.x[0]], zoom_start=12)
    folium.GeoJson(boundary, name="Urban Boundary", style_function=lambda x: {"color": "blue"}).add_to(m)
    folium.GeoJson(green_areas, name="Green Areas", style_function=lambda x: {"color": "green"}).add_to(m)
    folium.LayerControl().add_to(m)
    folium_static(m)

st.title("Urban Green Area Visualizer")
city_name = st.text_input("Enter a city name:", "Mysuru, India")
if st.button("Show Map"):
    display_map(city_name)
