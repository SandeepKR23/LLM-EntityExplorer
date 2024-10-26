import folium
import json
from shapely.geometry import mapping 
from shapely import wkt


def create_map_with_geojson(data):
    # Define the center of the map based on the first location in the JSON data
    first_location = data[0]['Geo_Locations'][0]  # Access the first location
    map_center = [first_location['Latitude'], first_location['Longitude']]  # Set map center

    # Create the map object
    m = folium.Map(location=map_center, zoom_start=5)

    # Function to add GeoJSON data to the map
    def add_geojson_to_map(m, geojson_data):
        folium.GeoJson(
            geojson_data,
            style_function=lambda x: {
                'fillColor': 'orange',
                'color': 'red',
                'weight': 2,
                'fillOpacity': 0.5,
            }
        ).add_to(m)
    
    for item in data:
      geojson_str = item['Geometry']  # Access the 'Geometry' field (WKT format string)

      # Convert WKT string to Shapely geometry
      shapely_geom = wkt.loads(geojson_str)  # Convert the WKT string to a Shapely object

      # Convert the Shapely geometry to a GeoJSON-like dict
      geojson_dict = mapping(shapely_geom)
      add_geojson_to_map(m, geojson_dict)
    
    return m

"""
if __name__ == "__main__":
    with open('results.json', 'r') as json_file:
        data = json.load(json_file)

    # Extract the 'GeoJSON Data' section
    geojson_data = data['GeoJSON Data']

    # Generate the map with GeoJSON data
    map_object = create_map_with_geojson(geojson_data)

    # Save the map as an HTML file
    map_object.save('map.html')
    print("Map saved as 'map.html'. Open this file in a web browser to view the map.")
"""