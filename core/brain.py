from core.config import config
import random

class Brain:
    def __init__(self):
        self.name = config.NAME
        self.llm_provider = config.LLM_PROVIDER
        
    def process(self, command):
        """Processes the user command and returns a response/action."""
        if not command:
            return None
            
        # Placeholder for LLM logic
        # For now, let's keep the greeting logic but fixed
        if any(word in command for word in ['hello', 'hi', self.name.lower()]):
            return f"Hello! I am {self.name}. How can I help you today?"
            
        return "I'm still learning. Soon I'll be able to help you with that using my LLM brain!"

brain = Brain()

