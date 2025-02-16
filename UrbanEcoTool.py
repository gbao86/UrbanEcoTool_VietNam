#!/usr/bin/env python
# coding: utf-8

# # Urban Green Space Analysis and Optimization Tool

# In[2]:


pip install streamlit


# In[3]:


import streamlit as st


# In[4]:


get_ipython().system('pip install osmnx geopandas folium matplotlib scikit-learn')


# In[5]:


pip install osmnx


# In[6]:


pip install folium


# In[7]:


pip install scikit-learn


# In[8]:


pip install streamlit-folium


# In[9]:


from shapely.geometry import Polygon


# In[10]:


import warnings
warnings.filterwarnings("ignore")


# In[11]:


import osmnx as ox
import geopandas as gpd
import pandas as pd
import folium
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


# In[12]:


# Function to fetch urban boundary and green area data
def fetch_urban_data(city_name):
    import osmnx as ox
    print(f"Fetching data for {city_name}...")
    
    # Fetch urban boundary
    boundary = ox.geocode_to_gdf(city_name)
    
    # Fetch all types of green areas suitable for planting trees
    green_tags = {
        "leisure": ["park", "garden"],
        "landuse": [ "grass", "meadow"],
        "natural": ["wood", "grassland"]
    }
    green_areas = ox.features_from_place(city_name, tags=green_tags)
    
    return boundary, green_areas

# Fetch data for a city(Mysuru)
city_name = "Mysuru, India"
boundary, green_areas = fetch_urban_data(city_name)

st.write(boundary.head())
st.write(green_areas.head())


# In[13]:


# Function to calculate green space coverage
def analyze_green_space(boundary, green_areas):
    green_areas['area_sqm'] = green_areas.geometry.area
    total_green_space = green_areas['area_sqm'].sum()
    boundary_area = boundary.geometry.area.iloc[0]
    coverage_percentage = (total_green_space / boundary_area) * 100
    
    st.write(f"Total Green Space: {total_green_space:.2f} sq.m")
    st.write(f"City Area: {boundary_area:.2f} sq.m")
    st.write(f"Green Space Coverage: {coverage_percentage:.2f}%")
    
    return total_green_space, coverage_percentage

# Analyze green space for the city
total_green_space, coverage_percentage = analyze_green_space(boundary, green_areas)


# In[14]:


# Function to predict environmental impact based on green space area
def predict_environmental_impact(green_space_areas, temperature_reductions):
    model = LinearRegression()
    green_space_areas = green_space_areas.values.reshape(-1, 1)
    temperature_reductions = temperature_reductions.values
    model.fit(green_space_areas, temperature_reductions)
    
    # Predict impact for 1000 sq.m of green space
    predicted_reduction = model.predict([[1000]])[0]
    st.write(f"Predicted Temperature Reduction for 1000 sq.m Green Space: {predicted_reduction:.2f}°C")
    return model

# Example data for prediction
green_space_data = pd.Series([100, 500, 1000, 1500, 2000])  # Green space areas in sq.m
temp_reduction_data = pd.Series([0.1, 0.5, 1.0, 1.5, 2.0])  # Corresponding temperature reductions in °C

# Train the model and predict
model = predict_environmental_impact(green_space_data, temp_reduction_data)


# In[15]:


from shapely.geometry import Polygon, MultiPolygon

# Function to create a map visualization
def visualize_data(boundary, green_areas, city_name):
    # Create a Folium map centered on the city's boundary centroid
    m = folium.Map(
        location=[boundary.geometry.centroid.y.iloc[0], boundary.geometry.centroid.x.iloc[0]], 
        zoom_start=12
    )
    
    # Add green areas to the map
    for _, row in green_areas.iterrows():
        geometry = row['geometry']
        
        # Check if the geometry is a Polygon
        if isinstance(geometry, Polygon):
            folium.Polygon(
                locations=[(pt[1], pt[0]) for pt in geometry.exterior.coords],
                color='green',
                fill=True,
                fill_opacity=0.5
            ).add_to(m)
        
        # Check if the geometry is a MultiPolygon
        elif isinstance(geometry, MultiPolygon):
            for polygon in geometry.geoms:  # Use .geoms to iterate over individual polygons
                folium.Polygon(
                    locations=[(pt[1], pt[0]) for pt in polygon.exterior.coords],
                    color='green',
                    fill=True,
                    fill_opacity=0.5
                ).add_to(m)
    
    # Save the map as an HTML file
    map_file = f"{city_name.replace(' ', '_')}_green_space_map.html"
    m.save(map_file)
    st.write(f"Map saved as {map_file}")
    return m

# Visualize the city's green spaces
map_result = visualize_data(boundary, green_areas, city_name)


# In[16]:


from streamlit_folium import folium_static

# Function to generate map
def display_map(city_name):
    st.subheader(f"Map of {city_name}")
    
    # Fetch urban boundary
    boundary = ox.geocode_to_gdf(city_name)
    
    # Fetch all types of green areas suitable for planting trees
    green_tags = {
        "leisure": ["park", "garden"],
        "landuse": ["grass", "meadow"],
        "natural": ["wood", "grassland"]
    }
    green_areas = ox.features_from_place(city_name, tags=green_tags)
    
    # Create folium map
    centroid = boundary.geometry.centroid.iloc[0]
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)
    
    # Add urban boundary to map
    folium.GeoJson(boundary, name="Urban Boundary", style_function=lambda x: {"color": "blue"}).add_to(m)
    
    # Add green areas to map
    folium.GeoJson(green_areas, name="Green Areas", style_function=lambda x: {"color": "green"}).add_to(m)
    
    # Display map in Streamlit
    folium_static(m)

# Streamlit UI
st.title("Urban Eco Tool")
city_name = st.text_input("Enter a city name:", "Mysuru, India")

if st.button("Show Map"):
    display_map(city_name)


# In[17]:


get_ipython().system('jupyter nbconvert --to script UrbanEcoTool.ipynb')

