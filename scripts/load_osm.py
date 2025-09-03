import json
from collections import Counter
import pprint

# Load the GeoJSON file
with open("data/OSM/export.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract features
features = geojson_data.get("features", [])

# Print number of features
print(f"Total number of features: {len(features)}")

# Print geometry types
geometry_types = Counter()
for feature in features:
    geom = feature.get("geometry", {})
    geometry_types[geom.get("type", "Unknown")] += 1

print("\nGeometry types:")
for geom_type, count in geometry_types.items():
    print(f"- {geom_type}: {count}")

# Collect all unique property keys
property_keys = set()
for feature in features:
    props = feature.get("properties", {})
    property_keys.update(props.keys())

print("\nUnique property keys (columns):")
# print properties with the number of counts
# for key in sorted(property_keys):
    # count = sum(1 for feature in features if key in feature.get("properties", {}))
    # print(f"- {key} - {count}")    


# Optional: Preview the first feature
# print("\nFirst feature preview:")
# pprint.pprint(features[0], depth=3)

# Filter properties of interest from a list
property_of_interest = ["name", "height", "height:hub", "manufacturer", "model", "operator", "rotor:diameter", "start_date", "was:power", "generator:output:electricity"]

filtered_features = []
for feature in features:
    props = feature.get("properties", {})
    filtered_props = {key: props[key] for key in property_of_interest if key in props}
    if filtered_props:
        filtered_feature = feature.copy()
        filtered_feature["properties"] = filtered_props
        filtered_features.append(filtered_feature)

# Create pandas dataframe with filtered_features
import pandas as pd
print(f"Number of rows after filtering properties: {len(filtered_features)}")
df = pd.json_normalize(filtered_features)
print(f"Number of rows after creating DataFrame: {len(df)}")
# Print the dataframe
print("\nFiltered DataFrame:")
print(df.head(20))
print(df.info())

# Keep only the rows with geometry.type "Point"
df = df[df["geometry.type"] == "Point"]
print(f"Number of rows after filtering geometry type 'Point': {len(df)}")

# reset index
# df.reset_index(drop=True, inplace=True)

# Separate the coordinates into latitude and longitude as other columns
df["Lon"] = df["geometry.coordinates"].apply(lambda x: x[0] if isinstance(x, list) else None)
df["Lat"] = df["geometry.coordinates"].apply(lambda x: x[1] if isinstance(x, list) else None)

# Rename columns
df.rename(columns={
    "properties.rotor:diameter": "Diameter",
    "properties.height:hub": "Hub Height",
    "properties.height": "Total Height",
    "properties.manufacturer": "Manufacturer",
    "properties.operator": "Operator",
    "properties.generator:output:electricity": "Rated Power",
    "properties.model": "Model",
    "properties.start_date": "Start Date",
}, inplace=True)

# if Rated Power is in kw convert to MW (it is a string)
def convert_power(value):
    if isinstance(value, str):
        # Normalize the string
        value = value.lower().strip().replace(",", ".")  # Replace comma with a point for decimals
        value = value.replace("(", "").replace(")", "").replace("estimated", "").strip()  # Remove extra text
        value = value.replace("dependent on ws-2b type", "").strip()  # Remove irrelevant text
        
        # Ensure there is a space between the number and the unit
        value = value.replace("kw", " kw").replace("mw", " mw").replace("gw", " gw").replace("w", " w")
        
        # Handle "nan" values explicitly
        if value == "nan":
            return None
        
        # Handle kilowatts (kW)
        if "kw" in value and not value.endswith("mw"):
            try:
                # Handle cases like '7.5k kW' or '7.5kW'
                if "k k" in value or "k" in value:
                    num = float(value.replace("k k", "").replace("k", "").strip())
                    return f"{round(num, 3):g} MW"  # Convert directly to MW
                num = float(value.replace("kw", "").strip())
                return f"{round(num / 1000, 3):g} MW"  # Convert kW to MW and format
            except ValueError:
                return None
        
        # Handle megawatts (MW)
        elif value.endswith("mw"):
            try:
                num = float(value.replace("mw", "").strip())
                return f"{round(num, 3):g} MW"  # Already in MW, format
            except ValueError:
                return None
        
        # Handle gigawatts (GW)
        elif value.endswith("gw"):
            try:
                num = float(value.replace("gw", "").strip())
                return f"{round(num * 1000, 3):g} MW"  # Convert GW to MW and format
            except ValueError:
                return None
        
        # Handle watts (W)
        elif value.endswith("w"):
            try:
                num = float(value.replace("w", "").strip())
                return f"{round(num / 1_000_000, 6):g} MW"  # Convert W to MW and format
            except ValueError:
                return None
        
        # Handle ranges (e.g., "100-200 MW")
        elif "-" in value:
            try:
                parts = value.split("-")
                num = (float(parts[0].strip()) + float(parts[1].strip())) / 2  # Average the range
                return f"{round(num, 3):g} MW"
            except (ValueError, IndexError):
                return None
        
        # Handle approximate values (e.g., "about 1kW")
        elif "about" in value:
            try:
                num = float(value.replace("about", "").replace("kw", "").replace("mw", "").strip())
                return f"{round(num / 1000, 3):g} MW" if "kw" in value else f"{round(num, 3):g} MW"
            except ValueError:
                return None
        
        # Handle pure numbers (assume MW or kW based on value)
        else:
            try:
                num = float(value)
                if num > 30:  # Assume kW if the number is greater than 30
                    return f"{round(num / 1000, 3):g} MW"
                else:  # Assume MW if the number is 30 or less
                    return f"{round(num, 3):g} MW"
            except ValueError:
                return None
    
    # Handle numeric types directly
    elif isinstance(value, (int, float)):
        if value != value:  # Check for NaN (float('nan') is not equal to itself)
            return None
        if value > 30:  # Assume kW if the number is greater than 30
            return f"{round(value / 1000, 3):g} MW"
        else:  # Assume MW if the number is 30 or less
            return f"{round(value, 3):g} MW"
    
    # Return None for invalid or unrecognized inputs
    return None

# df["Rated Power"] = df["Rated Power"].apply(convert_power)
# print(df["Rated Power"].unique())
# print(df["Rated Power"].value_counts(dropna=False))  # 627
# print(len(df["Rated Power"].unique()))


# Drop columns geometry
# df.drop(columns=["geometry.coordinates", "geometry.type"], inplace=True)

# convert diameter columns type to float or NaN
df["Diameter"] = pd.to_numeric(df["Diameter"], errors='coerce')
print(f"Number of rows after converting 'Diameter': {len(df)}")

print(df.columns)

# Save as csv file named wind_farms
df.to_csv("data/wind_farms.csv", index=False)