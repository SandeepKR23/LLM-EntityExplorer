# app.py
from typing import Dict, Any, Optional, List
import pandas as pd
import streamlit as st
import json
import logging
from dataclasses import dataclass
from src.components.event import ChatProcessor, ContentExtractor
from src.components.geolocation import GeoDataMethods
from src.components.visualize import create_map_with_geojson
from src.utils import load_model, setup_logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Ensure artifacts directory exists
ARTIFACTS_DIR = "artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

@dataclass
class ProcessingResult:
    """Data class to store processing results"""
    event_types: str
    entities: str
    names: str
    geojson_data: List[Dict]
    raw_text: str

class EntityExplorer:
    """Main class for processing and analyzing text data"""
    
    def __init__(self):
        try:
            self.client = load_model()
            self.chat_processor = ChatProcessor(self.client)
            self.content_extractor = ContentExtractor()
            self.geo_data_methods = GeoDataMethods()
        except Exception as e:
            logger.error(f"Failed to initialize EntityExplorer: {str(e)}")
            raise

    def validate_input(self, text: str) -> bool:
        """Validate user input text"""
        return bool(text and text.strip())

    def process_locations(self, locations_text: str) -> pd.DataFrame:
        """Process location data and return geodata DataFrame"""
        try:
            locations = self.content_extractor.extract_locations(locations_text)
            if isinstance(locations, str):
                locations = [locations]

            df_location = pd.DataFrame({"Event_Locations": locations})
            processed_df = self.geo_data_methods.process_event_locations(df_location)
            
            # Process geodata
            processed_df['Geo_Data'], processed_df['Geo_Locations'] = zip(
                *processed_df['Split_location'].apply(self.geo_data_methods.fetch_geojson_for_locations)
            )
            
            return self.geo_data_methods.categorize_geojson(processed_df)
        except Exception as e:
            logger.error(f"Error processing locations: {str(e)}")
            raise

    def process_text(self, text: str) -> Optional[ProcessingResult]:
        """Process input text and return structured results"""
        try:
            if not self.validate_input(text):
                raise ValueError("Input text cannot be empty.")

            # Process different aspects of the text
            event_types = self.content_extractor.extract_event_type(self.chat_processor.process_text(text, "event_type"))
            
            entities = self.content_extractor.extract_entities(self.chat_processor.process_text(text, "entities"))
            
            names = self.content_extractor.extract_names(self.chat_processor.process_text(text, "names"))

            # Process locations
            processed_locations_df = self.process_locations(self.chat_processor.process_text(text, "locations"))

            # Convert geometry to serializable format
            processed_locations_df['Geometry'] = processed_locations_df['Geometry'].apply(lambda x: x.wkt if hasattr(x, 'wkt') else str(x))

            return ProcessingResult(
                event_types=event_types,
                entities=entities,
                names=names,
                geojson_data=processed_locations_df[['Split_location', 'Geo_Locations', 'Geometry']].to_dict(orient="records"),
                raw_text=text
            )

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return None
        
def save_results(results: ProcessingResult, filename: str = "results.json"):
    """Save processing results to JSON file"""
    try:
        file_path = os.path.join(ARTIFACTS_DIR, filename)
        with open(file_path, "w") as json_file:
            json.dump(vars(results), json_file, indent=4)
        logger.info(f"Results saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        raise

def create_visualization(geojson_data: List[Dict], filename: str = "map.html"):
    """Create and save visualization"""
    try:
        file_path = os.path.join(ARTIFACTS_DIR, filename)
        map_object = create_map_with_geojson(geojson_data)
        map_object.save(file_path)
        logger.info(f"Map saved as {filename}")
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        raise


def cli_interface():
    """Command-line interface for the application"""
    setup_logging()
    explorer = EntityExplorer()
    
    try:
        user_input = input("Enter the article or text for analysis: ")
        results = explorer.process_text(user_input)
        
        if results:
            save_results(results)
            create_visualization(results.geojson_data)
            print("Analysis complete! Check results.json and map.html for output.")
        else:
            print("Error processing text. Please check the logs for details.")
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"An error occurred: {str(e)}")


def streamlit_interface():
    """Streamlit web interface for the application"""
    setup_logging()
    st.set_page_config(page_title="LLM Entity Explorer", layout="wide")
    
    st.title("LLM Entity Explorer")
    st.write("Enter the article or text for analysis:")
    
    explorer = EntityExplorer()
    
    user_input = st.text_area("Input Text", height=200)
    
    if st.button("Analyze"):
        try:
            with st.spinner("Processing..."):
                results = explorer.process_text(user_input)
                
            if results:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Extracted Information")
                    st.write("**Event Types:**", results.event_types)
                    st.write("**Entities:**", results.entities)
                    st.write("**Names:**", results.names)

                    # # Displaying unique locations as a single string without duplicates and brackets
                    # locations = list({loc["Split_location"] for loc in results.geojson_data})  # Remove duplicates
                    # st.write("**Locations:**", locations)

                    # Displaying unique locations with bullet points
                    locations = list({loc["Split_location"] for loc in results.geojson_data})  # Remove duplicates
                    st.markdown("**Locations:**")
                    for location in locations:
                        st.markdown(f"- {location}")
                
                with col2:
                    st.subheader("Geographical Data")
                    if results.geojson_data:
                        map_object = create_map_with_geojson(results.geojson_data)
                        map_object.save("temp_map.html")
                        st.components.v1.html(open("temp_map.html").read(), height=400)
                    else:
                        st.write("No geographical data found.")
                        
                # Add download buttons
                st.download_button(
                    label="Download Results (JSON)",
                    data=json.dumps(vars(results), indent=4),
                    file_name="results.json",
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Streamlit interface error: {str(e)}")

if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description="LLM Entity Explorer")
    # parser.add_argument("--web", action="store_true", help="Run in web interface mode")
    # args = parser.parse_args()
    
    # if args.web:
    #     streamlit_interface()
    # else:
    #     cli_interface()

    streamlit_interface()