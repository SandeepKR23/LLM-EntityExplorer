# src/utils.py
from openai import OpenAI
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional

def load_model() -> OpenAI:
    load_dotenv()

    api_key = os.getenv("DEEPINFRA_API_KEY")
    
    if not api_key:
        raise ValueError("DEEPINFRA_API_KEY environment variable is not set.")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )
        logging.info("API client initialized successfully")
        return client
    
    except Exception as e:
        logging.error(f"Failed to initialize API client: {str(e)}")
        raise


def setup_logging(log_file: Optional[str] = None) -> None:
    if log_file is None:
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = f'llm_explorer_{timestamp}.log'

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Create logger instance
    logger = logging.getLogger(__name__)
    logger.info('Logging setup completed')
