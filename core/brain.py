from core.config import config
import os
import re
from core.skill_manager import skill_manager

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
        """Initializes the LLM and dynamically injects loaded skills into the prompt."""
        self.system_prompt = (
            f"You are {self.name}, an intelligent Linux Virtual Assistant. "
            "You have access to system tools. If a user asks for something you can do with a tool, "
            "respond ONLY with the tool command in the format: [TOOL_CALL: tool_name] "
            "Do not add any other text if you are calling a tool. "
            "Here are your currently installed tools:\n"
            f"{skill_manager.get_tool_descriptions()}\n\n"
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
        """Tiered Intent Pipeline implementation."""
        if not command:
            return None
            
        # --- TIER 1: Direct Match (Zero Latency) ---
        direct_tool = skill_manager.get_direct_match(command)
        if direct_tool:
            print(f"System: Direct Match found for '{direct_tool}'")
            return skill_manager.execute(direct_tool)

        # --- TIER 3: LLM Fallback (Reasoning) ---
        if self.llm_ready:
            llm_response = self._call_llm(command)
            
            # Check for Tool Call pattern: [TOOL_CALL: name]
            tool_match = re.search(r"\[TOOL_CALL:\s*(\w+)\]", llm_response)
            if tool_match:
                tool_name = tool_match.group(1)
                print(f"System: LLM suggested tool '{tool_name}'")
                return skill_manager.execute(tool_name)
            
            return llm_response
            
        return "I heard you, but I couldn't find a direct skill match and my LLM brain isn't configured."

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
            return f"Thinking error: {e}"

brain = Brain()
