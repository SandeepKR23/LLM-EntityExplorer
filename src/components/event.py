import re
from shapely.geometry import shape
from typing import List, Optional, Dict, Any
import logging
import requests
from src.components.Prompt_template import PromptTemplateGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatProcessor:
    def __init__(
            self, 
            client: Any, 
            model_name: str="microsoft/WizardLM-2-8x22B",
            llama_model_name :str  = "meta-llama/Meta-Llama-3.1-70B-Instruct",
            max_tokens: int = 256,
            temperature: float = 0.1,
            ):
        self.client = client
        self.model_name = model_name
        self.llama_model_name  = llama_model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _get_model_for_prompt(self, prompt_type: str) -> str:
        """
        Determine which model to use based on prompt type.
        """
        llama_prompt_types = ["event_type", "entities", "names", "phone_numbers"]
        return self.llama_model_name if prompt_type in llama_prompt_types else self.model_name
    
    def _get_prompt_content(self, text: str, prompt_type: str) -> str:
        """
        Get appropriate prompt content based on type.
        """
        if prompt_type == "event_type":
            return PromptTemplateGenerator.generate_event_type_prompt(text)
        elif prompt_type == "entities":
            return PromptTemplateGenerator.generate_entities_prompt(text)
        elif prompt_type == "names":
            return PromptTemplateGenerator.generate_names_prompt(text)
        elif prompt_type == "locations":
            return PromptTemplateGenerator.generate_event_location_prompt(text)
        elif prompt_type == "phone_numbers":
            return PromptTemplateGenerator.generate_phone_number_prompt(text)
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")


    def process_text(self, text: str, prompt_type: str):

        try:
            # Get the appropriate model and prompt content
            model_name = self._get_model_for_prompt(prompt_type)
            message_content = self._get_prompt_content(text, prompt_type)  # Fixed: Changed from _get_model_for_prompt

            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message_content}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise



class ContentExtractor:
    @staticmethod
    def extract_event_type(text: str) -> str:
        """Extract event types from text."""
        try:
            event_type_matches = re.findall(r"Event Type:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            event_types = []
            for match in event_type_matches:
                event_types.extend([etype.strip() for etype in match.split(',')])
            return ', '.join(event_types)
        except Exception as e:
            logger.error(f"Error extracting event types: {e}")
            return ""
    
    @staticmethod    
    def extract_entities(text):
        """Extract entities from text."""
        try:
            entities_matches = re.findall(r"Entities:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            entities = []
            for match in entities_matches:
                for entity in match.split(','):
                    cleaned_entity = re.sub(r'\s*\([^)]*\)', '', entity.strip())
                    entities.append(cleaned_entity)
            return ', '.join(entities)
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return ""
        
    @staticmethod    
    def extract_names(text):
        """Extract names using the same logic as entities."""
        try:
            entities_matches = re.findall(r"Entities:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            entities = []
            for match in entities_matches:
                for entity in match.split(','):
                    cleaned_entity = re.sub(r'\s*\([^)]*\)', '', entity.strip())
                    entities.append(cleaned_entity)
            return ', '.join(entities)
        except Exception as e:
            logger.error(f"Error extracting names: {e}")
            return ""
        
    @staticmethod
    def extract_locations(text):
        try:
            locations_match = re.findall(r'Event Locations?:\s*(\[.*?\])', text, re.IGNORECASE | re.MULTILINE)
            if locations_match:
                locations = locations_match[0].strip(';').strip()
                return locations if locations else []
            return []
        except Exception as e:
            logger.error(f"Error extracting locations: {e}")
            return []    


    @staticmethod
    def extract_emails(text: str) -> str:
        """Extract email addresses from text."""
        try:
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
            return ', '.join(emails) if emails else "None"
        except Exception as e:
            logger.error(f"Error extracting emails: {e}")
            return "None"
        
    @staticmethod 
    def extract_phone_numbers(text):
        try:
            # Adjust regex to match "Phone Numbers" instead of "Phone_Numbers"
            phone_numbers_match = re.search(r'Phone Numbers:\s*(.*)', text, re.IGNORECASE)
            if phone_numbers_match:
                return phone_numbers_match.group(1).strip()  # Return extracted phone numbers
            return "No phone numbers found."  # If no match found
        except Exception as e:
            logger.error(f"Error extracting phone numbers: {e}")
            return ""
      
    """Regex approach""",
    """
    @staticmethod 
    def extract_phone_numbers(text):
        try:
            # Regex pattern to match various phone number formats
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}|\d{4}'
            phone_numbers_matches = re.findall(phone_pattern, text)

            # Format the extracted phone numbers
            formatted_numbers = []
            for number in phone_numbers_matches:
                # Clean the number of any surrounding whitespace
                number = number.strip()

                # If it's a 10-digit number, format it as (XXX) XXX-XXXX
                cleaned_number = re.sub(r'[^0-9]', '', number)  # Remove all non-numeric characters
                if len(cleaned_number) == 10:  # Check if it's a valid 10-digit number
                    formatted_numbers.append(f"({cleaned_number[:3]}) {cleaned_number[3:6]}-{cleaned_number[6:]}")
                else:
                    formatted_numbers.append(number)  # Keep other formats as they are
            
            return ', '.join(formatted_numbers)
        except Exception as e:
            logger.error(f"Error extracting phone numbers: {e}")
            return ""
    """
