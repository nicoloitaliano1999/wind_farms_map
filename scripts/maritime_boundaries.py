# Read shp file

import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from shapely.geometry import Polygon, MultiPolygon
import json

# Load the shapefile
shapefile_path = "data/maritime_boundaries/eez_boundaries_v12.shp"
# load
eez = gpd.read_file(shapefile_path)

df = pd.read_csv("data/wind_farms.csv")

# plot in a map the boundaries
# eez.plot(figsize=(15, 10))
# plt.title("Maritime Boundaries")
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.grid(True)
# plt.show()

# Add a column country if the turbine in df are located within the eez boundaries of a specific country
def get_country(lat, lon):
    # Create a Point object
    point = Point(lon, lat)
    
    # Use vectorized operation to check which geometry contains the point
    mask = eez['geometry'].contains(point)
    
    # Return the country name if a match is found
    if mask.any():
        return eez.loc[mask, 'Country'].values[0]
    
    return None

df['Country'] = df.apply(lambda row: get_country(row['Lat'], row['Lon']), axis=1)

# Save the updated dataframe
df.to_csv("data/wind_farms_with_countries.csv", index=False)
