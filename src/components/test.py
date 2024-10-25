import folium
import pandas as pd
import json

def create_map_with_geojson(df_expanded):
    # Define the center of the map, you might want to adjust this based on the locations
    first_location = df_expanded['Geo_Locations'].iloc[0][0]  # Access the first location in the first row
    map_center = [first_location['Latitude'], first_location['Longitude']]  # Set map center to first location

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

    # Loop through the DataFrame and add each geometry to the map
    for index, row in df_expanded.iterrows():
        geojson_str = row['Geometry']  # Access the 'Geometry' column for each row
        print(geojson_str)
        add_geojson_to_map(m, geojson_str)  # Add the GeoJSON data to the map
    
    return m


if __name__ == "__main__":

    with open('results.json', 'r') as json_file:
        data = json.load(json_file)

    print(data[0]['Geo_Locations'][0])

    """
    # Convert the 'GeoJSON Data' from the JSON into a DataFrame
    df_location = pd.DataFrame(data['GeoJSON Data'])

    # Convert 'Geo_Locations' if it's in string format
    if isinstance(df_location['Geo_Locations'].iloc[0], str):
        df_location['Geo_Locations'] = df_location['Geo_Locations'].apply(lambda x: json.loads(x.replace("'", '"')))

    # Generate the map with GeoJSON data
    map_object = create_map_with_geojson(df_location)

    # Save the map as an HTML file
    map_object.save('map.html')
    print("Map saved as 'map.html'. Open this file in a web browser to view the map.")
    """
    #df_location = pd.read_csv("location.csv")
    # df_location = df_location.dropna(subset=['Geometry'])

    # # Convert 'Geo_Locations' if it's in string format
    # if isinstance(df_location['Geo_Locations'].iloc[0], str):
    #     df_location['Geo_Locations'] = df_location['Geo_Locations'].apply(lambda x: json.loads(x.replace("'", '"')))

    # mx = create_map_with_geojson(df_location)
    # mx.save('map.html')  # Save the map as an HTML file
    # print("Map saved as 'map.html'. Open this file in a web browser to view the map.")
