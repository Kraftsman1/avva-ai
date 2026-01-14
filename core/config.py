import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Assistant Settings
    NAME = os.getenv("AVVA_NAME", "Ava")
    WAKE_WORD = os.getenv("AVVA_WAKE_WORD", "Ava")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google") # google, openai, ollama
    API_KEY = os.getenv("LLM_API_KEY", "")
    MODEL_NAME = os.getenv("LLM_MODEL", "gemini-1.5-flash") # default for google
    
    # Locale
    LANGUAGE = os.getenv("AVVA_LANG", "en-uk")

config = Config()
