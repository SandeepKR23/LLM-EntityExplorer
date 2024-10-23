import re
from shapely.geometry import shape
import requests
from src.components import Prompt_template

class ChatProcessor:
    def __init__(self, client, model_name="microsoft/WizardLM-2-8x22B"):
        self.client = client
        self.model_name = model_name

    def process_text(self, text, prompt_type, temperature=0.1):
        if prompt_type == "event_type":
            message_content = Prompt_template.PromptTemplateGenerator.generate_event_type_prompt(text)
        elif prompt_type == "entities":
            message_content = Prompt_template.PromptTemplateGenerator.generate_entities_prompt(text)
        elif prompt_type == "names":
            message_content = Prompt_template.PromptTemplateGenerator.generate_names_prompt(text)
        elif prompt_type == "locations":
            message_content = Prompt_template.PromptTemplateGenerator.generate_event_location_prompt(text)
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": message_content}],
            temperature=temperature,
            max_tokens=256,
        )
        generated_text = response.choices[0].message.content
        return generated_text


class ContentExtractor:
    @staticmethod
    def extract_event_type(text):
        try:
            event_type_matches = re.findall(r"Event Type:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            event_types = []
            for match in event_type_matches:
                event_types.extend([etype.strip() for etype in match.split(',')])
            return ', '.join(event_types)
        except Exception as e:
            print(f"Error extracting event types: {e}")
            return ""
    
    @staticmethod    
    def extract_entities(text):
        try:
            entities_matches = re.findall(r"Entities:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            entities = []
            for match in entities_matches:
                for entity in match.split(','):
                    cleaned_entity = re.sub(r'\s*\([^)]*\)', '', entity.strip())
                    entities.append(cleaned_entity)
            return ', '.join(entities)
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return ""
        
    @staticmethod    
    def extract_names(text):
        try:
            entities_matches = re.findall(r"Entities:\s*(.*)", text, re.IGNORECASE | re.MULTILINE)
            entities = []
            for match in entities_matches:
                for entity in match.split(','):
                    cleaned_entity = re.sub(r'\s*\([^)]*\)', '', entity.strip())
                    entities.append(cleaned_entity)
            return ', '.join(entities)
        except Exception as e:
            print(f"Error extracting entities: {e}")
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
            print(f"Error extracting locations: {e}")
            return []    
