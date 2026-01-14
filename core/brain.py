from core.config import config
import datetime
import random
import os

class Brain:
    def __init__(self):
        self.name = config.NAME
        self.llm_provider = config.LLM_PROVIDER.lower()
        self.api_key = config.API_KEY
        self.model_name = config.MODEL_NAME
        
        # Initialize LLM client if API key is provided
        self.llm_ready = False
        if self.api_key and self.api_key != "your_api_key_here":
            self._init_llm()

    def _init_llm(self):
        """Initializes the selected LLM provider."""
        try:
            if self.llm_provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                # Set up system prompt
                self.chat = self.model.start_chat(history=[])
                system_prompt = f"You are {self.name}, an intelligent Linux Virtual Assistant. Be concise and helpful."
                self.chat.send_message(system_prompt)
                self.llm_ready = True
            elif self.llm_provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.llm_ready = True
            # Add more providers (Ollama, Anthropic) here
        except Exception as e:
            print(f"Error initializing LLM ({self.llm_provider}): {e}")

    def process(self, command):
        """Processes the user command and returns a response/action."""
        if not command:
            return None
            
        # 1. Local Intent Matching (Fast & Offline)
        local_response = self._match_local_intent(command)
        if local_response:
            return local_response

        # 2. LLM Processing (Intelligent)
        if self.llm_ready:
            return self._call_llm(command)
            
        # 3. Final Fallback
        return "I heard you, but I don't have a local skill for that and my LLM brain isn't configured yet."

    def _match_local_intent(self, command):
        """Checks for commands that can be handled without an LLM."""
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
            
        return None

    def _call_llm(self, command):
        """Sends the command to the configured LLM provider."""
        try:
            if self.llm_provider == "google":
                response = self.chat.send_message(command)
                return response.text
            elif self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": f"You are {self.name}, a Linux Virtual Assistant."},
                        {"role": "user", "content": command}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"I ran into an issue while thinking: {e}"

brain = Brain()
