class PromptTemplateGenerator:
    @staticmethod
    def generate_event_type_prompt(text):
        return f"""
        You are a Risk Analyst expert in identifying and listing the event types mentioned in the provided article.

        Article:
        "{text}"

        Instructions:
        - Read the article carefully.
        - Identify and list the relevant event types, focusing solely on the information provided in the article.

        Task:
        Event Type: Identify and list the standard event types mentioned in the article. Focus on broad, generic classifications and exclude specific event titles or descriptions. Use commas to separate multiple event types.

        Example:
        Event Type: Earthquake, Child Labour, Deaths, Access to Water, Land Rights

        Note:
        - Do not include any non-relevant details or additional commentary.
        - Ensure the response is concise and directly answers the task requirements.

        Answer:
        """

    @staticmethod
    def generate_entities_prompt(text):
        return f"""
        You are a Risk Analyst expert in identifying and listing the entities (companies and organizations) mentioned in the provided article.

        Article:
        "{text}"

        Instructions:
        - Carefully analyze the article.
        - Identify and list all relevant entities (companies and organizations) mentioned.
        - Focus solely on the information provided in the article.

        Task:
        Entities: List all companies and organizations mentioned in the article. This includes:
        - For-profit companies
        - Non-profit organizations
        - Government agencies
        - International bodies
        - Educational institutions
        - Research institutes
        - Industry associations

        Guidelines:
        - Separate multiple entities with commas.
        - Include the full, official name of each entity.
        - If an acronym is used, include both the full name and the acronym in parentheses.
        - Exclude specific event titles, product names, or descriptions.
        - Do not include countries, cities, or other geographical entities unless they are part of an organization's name.
        - If an entity is mentioned multiple times, list it only once.
        - If unsure about an entity, include it and note your uncertainty.
        - Do not include any non-relevant details or additional commentary.

        Example:
        Entities: Apple Inc., Microsoft Corporation, World Health Organization (WHO), United Nations Children's Fund (UNICEF), U.S. Department of Energy, European Union (EU), Harvard University, International Red Cross and Red Crescent Movement

        Note:
        - Provide only the requested information without additional commentary, explanations, or notes.
        - Ensure your response is concise and directly addresses the task requirements.

        Answer:
        """

    @staticmethod
    def generate_names_prompt(text):
        return f"""
        You are a Risk Analyst expert in identifying and listing the entities (mentioned persons names) in the provided article.

        Article:
        "{text}"

        Instructions:
        - Carefully analyze the article.
        - Identify and list all relevant entities (persons names) mentioned.
        - Focus solely on the information provided in the article.

        Task:
        Entities: List all persons names mentioned in the article.

        Example:
        Entities: Elon Musk, John Doe, Sandeep Raj, Bill Gates, Steve Jobs, Mohammad Azharuddin

        Note:
        - Provide only the requested information without additional commentary, explanations, or notes.
        - Ensure your response is concise and directly addresses the task requirements.

        Answer:
        """
    
    @staticmethod
    def generate_event_location_prompt(text):
        return f"""
        You are an expert in extracting geographical event locations from articles. Analyze the following text and extract locations:

        Article:
        {text}

        Instructions:
        1. Carefully read the article.
        2. Extract only geographical locations mentioned in the context of the event.
        3. Include primary event locations and other affected locations.
        4. List cities, countries, states, and regions as applicable.
        5. Exclude non-geographical entities like organizations or company names.
        6. Do not add any information not explicitly stated in the article.

        Output Format:
        Event Locations: [City1, Country1; City2, State2, Country2; Region3; Country4]

        Rules:
        - Separate different locations with semicolons (;)
        - For locations within the same country, use commas (,)
        - List only unique locations (no duplicates)
        - Do not include any explanations or additional commentary
        - If no locations are mentioned, respond with "No specific locations mentioned"

        Example Output:
        Event Locations: [New York City, USA; Paris, France; Tokyo, Japan; California, USA; Middle East]

        Your Response:
        """

    @staticmethod
    def generate_phone_number_prompt(text):
        return f"""
        You are a data extraction expert specializing in identifying and listing phone numbers from the provided text.

        Text:
        "{text}"

        Instructions:
        - Read the text carefully.
        - Identify and list all the phone numbers mentioned in the text.
        - Ensure to capture various formats, including country codes and different separators.

        Task:
        Phone Numbers: Identify and list all phone numbers found in the text. Use commas to separate multiple phone numbers.

        Example:
        Phone Numbers: (123) 456-7890, +1 234 567 8901, 987-654-3210

        Note:
        - Do not include any non-relevant details or additional commentary.
        - Ensure the response is concise and directly answers the task requirements.

        Answer:
        """
