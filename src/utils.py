from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")

if DEEPINFRA_API_KEY is None:
    raise ValueError("DEEPINFRA_API_KEY environment variable is not set.")

print("API Key loaded successfully.")

def load_model():
    client = OpenAI(
        api_key=DEEPINFRA_API_KEY,
        base_url="https://api.deepinfra.com/v1/openai",
    )
    return client


if __name__== "__main__":
    val = load_model()
    print(val)