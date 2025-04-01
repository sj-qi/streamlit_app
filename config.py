import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys for LLM
API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database Credentials
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Generic Variables
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")