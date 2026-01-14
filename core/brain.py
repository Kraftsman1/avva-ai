from core.config import config
import datetime
import random

class Brain:
    def __init__(self):
        self.name = config.NAME
        self.llm_provider = config.LLM_PROVIDER
        self.api_key = config.API_KEY
        
    def process(self, command):
        """Processes the user command and returns a response/action."""
        if not command:
            return None
            
        # 1. Local Intent Matching (Works without API Keys)
        if any(word in command for word in ['hello', 'hi', self.name.lower()]):
            return f"Hello! I am {self.name}. How can I help you today?"
            
        if 'time' in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now}."
            
        if 'date' in command:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        if 'who are you' in command or 'your name' in command:
            return f"I am {self.name}, your Linux Virtual Assistant."

        # 2. LLM Processing (Requires API Key)
        if self.api_key and self.api_key != "your_api_key_here":
            # This is where we will call the LLM in the next step
            return "I have an API key, so I could talk to my LLM brain here. (LLM integration coming soon!)"
            
        # 3. Final Fallback
        return "I heard you, but I don't have a specific local skill for that yet, and no LLM API key is configured."

brain = Brain()

