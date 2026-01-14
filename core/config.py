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
    MODEL_NAME = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # TTS Settings: gtts, piper, openai, elevenlabs
    TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", API_KEY)
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    PIPER_VOICE = os.getenv("PIPER_VOICE", "en_US-lessac-medium")
    
    # Locale
    LANGUAGE = os.getenv("AVVA_LANG", "en-uk")

config = Config()
