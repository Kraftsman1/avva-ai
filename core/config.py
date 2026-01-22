import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (Defaults)
load_dotenv()

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "avva"
        self.config_file = self.config_dir / "config.json"
        
        # Load Defaults from Env
        self.defaults = {
            "NAME": os.getenv("AVVA_NAME", "Ava"),
            "WAKE_WORD": os.getenv("AVVA_WAKE_WORD", "Ava"),
            "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "google"),
            "API_KEY": os.getenv("LLM_API_KEY", ""),
            "MODEL_NAME": os.getenv("LLM_MODEL", "gemini-1.5-flash"),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "TTS_ENGINE": os.getenv("TTS_ENGINE", "gtts"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "LANGUAGE": os.getenv("AVVA_LANG", "en-uk"),
            "PIPER_VOICE": os.getenv("PIPER_VOICE", "en_US-lessac-medium.onnx")
        }
        
        # Override with User Config
        self.user_config = {}
        self._load_user_config()
        self._apply_config()

    def _load_user_config(self):
        """Loads user overrides from JSON."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.user_config = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading config.json: {e}")

    def _apply_config(self):
        """Applies merged config to class attributes."""
        # Merge: User > Env/Defaults
        merged = {**self.defaults, **self.user_config}
        
        self.NAME = merged["NAME"]
        self.WAKE_WORD = merged["WAKE_WORD"]
        self.LLM_PROVIDER = merged["LLM_PROVIDER"]
        self.API_KEY = merged["API_KEY"]
        self.MODEL_NAME = merged["MODEL_NAME"]
        self.OLLAMA_HOST = merged["OLLAMA_HOST"]
        self.TTS_ENGINE = merged["TTS_ENGINE"]
        self.OPENAI_API_KEY = merged["OPENAI_API_KEY"]
        self.LANGUAGE = merged["LANGUAGE"]
        self.PIPER_VOICE = merged["PIPER_VOICE"]

    def save_config(self, key, value):
        """Updates a setting and saves to JSON."""
        self.user_config[key] = value
        
        # Ensure dir exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.user_config, f, indent=4)
            
            # Re-apply to current instance
            self._apply_config()
            return True
        except Exception as e:
            print(f"custom_error: Failed to save config: {e}")
            return False

config = Config()
