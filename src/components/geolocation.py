from openai import OpenAI
import pandas as pd
import re
import numpy as np
import requests
from shapely.geometry import shape
from shapely.geometry import Point
import json
from datetime import datetime

class GeoDataMethods:
    """Methods for processing geographical data."""

    @staticmethod
    def process_event_locations(df_location: pd.DataFrame, location_column: str = 'Event_Locations') -> pd.DataFrame:
        # Step 1: Replace NaN with an empty list and split locations in one go
        df_location = df_location.assign(
            Split_location=df_location[location_column].apply(
                lambda x: [loc.strip() for loc in str(x).replace('[', '').replace(']', '').split(';')]
                if isinstance(x, str) and len(x) > 0 else []
            )
        )

        # Step 2: Explode the DataFrame and filter out empty rows
        df_location = df_location.explode('Split_location').reset_index(drop=True)
        df_location = df_location[df_location['Split_location'].notna() & (df_location['Split_location'] != '')]

        return df_location 

    
    # GeoAPI function to fetch GeoJSON data
    @staticmethod
    def geoapi(location: str) -> list:
        url = f"https://nominatim.openstreetmap.org/search.php?q={location}&accept-language=en&polygon_geojson=1&limit=2&format=jsonv2"
        headers = {
            "User-Agent": "geojson_converter/1.0 (sandeep@intuitive-ai.com)"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error fetching data for {location}: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {location}: {e}")
            return None

    # Fetch GeoJSON data for each location
    @staticmethod
    def fetch_geojson_for_locations(location: str) -> tuple:
        geojson_data = []
        geojson_location = []
        data = GeoDataMethods.geoapi(location)
        if data:
            for item in data:
                if 'lat' in item and 'lon' in item:
                    geojson_location.append({
                        'Location': location,
                        'Latitude': float(item['lat']),
                        'Longitude': float(item['lon'])
                    })
            geojson_data = data  # Assign the entire response to geojson_data
        return geojson_data, geojson_location

    @staticmethod
    def categorize_geojson(df_location: pd.DataFrame) -> pd.DataFrame:
        # Initialize the 'Geometry' column if it doesn't already exist
        if 'Geometry' not in df_location.columns:
            df_location['Geometry'] = None

        for index, row in df_location.iterrows():
            items = row['Geo_Data']
            
            if not items:
                continue  # Skip if there is no Geo_Data

            # Initialize a variable to hold the shape to be assigned
            selected_shape = None

            for item in items:
                geojson = item.get('geojson', {})
                geojson_type = geojson.get('type', '')

                # Determine which shape to use
                if geojson_type in ['MultiPolygon', 'Polygon']:
                    selected_shape = shape(geojson)
                    # Break loop if we found a MultiPolygon or Polygon
                    break
                elif geojson_type == 'Point':
                    # Assign Point if no other shape has been selected
                    if selected_shape is None:
                        selected_shape = shape(geojson)

            # Assign the selected shape to the 'Geometry' column
            df_location.at[index, 'Geometry'] = selected_shape
        return df_location
