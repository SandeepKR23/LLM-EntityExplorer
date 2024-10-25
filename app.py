from src.components import event
from src import utils
from src.components import geolocation
import pandas as pd
import streamlit as st
import json
from src.components import visualize

def process_user_input(user_input_text):
    try:
        # Load the model
        client = utils.load_model()
        chat_processor = event.ChatProcessor(client)
        content_extractor = event.ContentExtractor()
        geo_data_methods = geolocation.GeoDataMethods()

        results = {}

        if not user_input_text.strip():
            return {"error": "Input text cannot be empty."}
        
        # Processing event types
        event_types_result = content_extractor.extract_event_type(chat_processor.process_text(user_input_text, "event_type"))
        results['Event Types'] = event_types_result

        # Processing entities (companies/organizations)
        entities_result = content_extractor.extract_entities(chat_processor.process_text(user_input_text, "entities"))
        results['Entities (Companies/Organizations)'] = entities_result

        # Processing names (persons)
        names_result = content_extractor.extract_names(chat_processor.process_text(user_input_text, "names"))
        results['Names (Persons)'] = names_result

        # Processing locations
        locations_text = chat_processor.process_text(user_input_text, "locations")
        locations = content_extractor.extract_locations(locations_text)

        # If locations is a scalar or string, wrap it in a list
        if isinstance(locations, str):
            locations = [locations]

        # Convert locations into a DataFrame for geolocation processing
        df_location = pd.DataFrame({"Event_Locations": locations})
        processed_locations_df = geo_data_methods.process_event_locations(df_location)
        
        # Fetch GeoJSON for locations
        processed_locations_df['Geo_Data'], processed_locations_df['Geo_Locations'] = zip(*processed_locations_df['Split_location'].apply(geo_data_methods.fetch_geojson_for_locations))

        # Categorize and add GeoJSON geometry shapes
        processed_locations_df = geo_data_methods.categorize_geojson(processed_locations_df)


        # Convert the Geometry (MultiPolygon) to a serialized form (e.g., WKT or GeoJSON)
        processed_locations_df['Geometry'] = processed_locations_df['Geometry'].apply(lambda x: x.wkt if hasattr(x, 'wkt') else str(x))

        # Store results in the final results dictionary
        results['GeoJSON Data'] = processed_locations_df[['Split_location', 'Geo_Locations', 'Geometry']].to_dict(orient="records")

        return results
    

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # User input
    user_input_text = input("Enter the article or text for analysis: ")

    # Process the input and get the results
    output = process_user_input(user_input_text)

    # Save the results to a JSON file for easy access later
    with open("results.json", "w") as json_file:
        json.dump(output, json_file, indent=4)

    print("Results have been saved to 'results.json'")

    with open('results.json', 'r') as json_file:
        data = json.load(json_file)

    # Extract the 'GeoJSON Data' section
    geojson_data = data['GeoJSON Data']

    # Generate the map with GeoJSON data
    map_object = visualize.create_map_with_geojson(geojson_data)

    # Save the map as an HTML file
    map_object.save('map.html')
    print("Map saved as 'map.html'. Open this file in a web browser to view the map.")

    

# def main():
#     st.title("LLM Entity Explorer")
#     st.write("Enter the article or text for analysis:")

#     # User input
#     user_input_text = st.text_area("Input Text", height=200)

#     if st.button("Analyze"):
#         output = process_user_input(user_input_text)

#         # Display results
#         if "error" in output:
#             st.error(output['error'])
#         else:
#             st.subheader("Results")
#             for key, value in output.items():
#                 st.markdown(f"**{key}:** {value}")

# if __name__ == "__main__":
#     main()