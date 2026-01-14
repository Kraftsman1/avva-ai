from core.config import config
import datetime
import os
import re
from core.tool_registry import execute_tool, get_tools_description

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
        """Initializes the selected LLM provider with Tool Use instructions."""
        self.system_prompt = (
            f"You are {self.name}, an intelligent Linux Virtual Assistant. "
            "You have access to specific system tools. If a user asks for something you can do with a tool, "
            "respond ONLY with the tool command in the format: [TOOL_CALL: tool_name] "
            "Do not add any other text if you are calling a tool. "
            "Here are your available tools:\n"
            f"{get_tools_description()}\n\n"
            "If no tool is appropriate, respond naturally in a helpful and concise way."
        )

        try:
            if self.llm_provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.chat = self.model.start_chat(history=[])
                self.chat.send_message(self.system_prompt)
                self.llm_ready = True
            elif self.llm_provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.llm_ready = True
        except Exception as e:
            print(f"Error initializing LLM ({self.llm_provider}): {e}")

    def process(self, command):
        """Processes the user command and routes to LLM or Local skills."""
        if not command:
            return None
            
        # For certain critical/fast commands, we can still use local matching to save latency
        if any(word in command for word in ['hello', 'hi', self.name.lower()]):
            return f"Hello! I am {self.name}. How can I help you today?"

        # 2. LLM Processing with Tool Extraction
        if self.llm_ready:
            llm_response = self._call_llm(command)
            
            # Check for Tool Call pattern: [TOOL_CALL: name]
            tool_match = re.search(r"\[TOOL_CALL:\s*(\w+)\]", llm_response)
            if tool_match:
                tool_name = tool_match.group(1)
                print(f"System: Executing tool '{tool_name}'...")
                return execute_tool(tool_name)
            
            return llm_response
            
        # 3. Final Fallback (Simulate local matching if LLM is offline)
        return "I heard you, but my LLM brain isn't configured, and I don't have a local regex for that yet."

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
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": command}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"I ran into an issue while thinking: {e}"

brain = Brain()
