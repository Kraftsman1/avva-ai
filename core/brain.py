from core.config import config
import os
import json
import re
from core.skill_manager import skill_manager
from core.persistence import storage

class Brain:
    def __init__(self):
        self.name = config.NAME
        self.llm_provider = config.LLM_PROVIDER.lower()
        self.api_key = config.API_KEY
        self.model_name = config.MODEL_NAME
        
        # Initialize LLM client
        self.llm_ready = False
        if (self.api_key and self.api_key != "your_api_key_here") or self.llm_provider == "ollama":
            self._init_llm()

    def _init_llm(self):
        """Initializes the LLM and dynamically injects loaded skills into the prompt."""
        self.system_prompt = (
            f"You are {self.name}, an intelligent Linux Virtual Assistant. "
            "Your goal is to extract intent and arguments from user commands. "
            "You MUST respond ONLY with a valid JSON object in the following format:\n"
            "{\n"
            "  \"intent\": \"tool_name\",\n"
            "  \"arguments\": {\"param1\": \"value\"},\n"
            "  \"confidence\": 0.95,\n"
            "  \"natural_response\": \"Optional helpful message\"\n"
            "}\n"
            "If no tool is appropriate, set intent to null and provide a conversational natural_response.\n"
            "Here are your currently installed tools:\n"
            f"{skill_manager.get_tool_descriptions()}\n\n"
            "STRICT RULES:\n"
            "1. Output ONLY JSON.\n"
            "2. Confidence must be between 0.0 and 1.0.\n"
            "3. If multiple tools fit, choose the best one."
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
            elif self.llm_provider == "ollama":
                import ollama
                # Warm up and Verify
                # We do a tiny request to load the model into VRAM
                ollama.chat(model=self.model_name, messages=[{"role": "user", "content": "hi"}], options={"num_predict": 1})
                self.llm_ready = True
                self.messages = [{"role": "system", "content": self.system_prompt}]
                print(f"System: Ollama backend optimized & ready (Model: {self.model_name})")
        except Exception as e:
            print(f"Error initializing LLM ({self.llm_provider}): {e}")

    def process(self, command):
        """Tiered Intent Pipeline implementation."""
        if not command:
            return None
            
        # Log User Query
        storage.log_interaction("user", command)
        
        response = self._get_response(command)
        
        # Log Assistant Response
        if response:
            res_text = response.get("text") if isinstance(response, dict) else str(response)
            tool_call = response.get("exec_str") if isinstance(response, dict) else None # We should probably store exec_str in result
            storage.log_interaction("avva", res_text, tool_call)
            
        return response

    def _get_response(self, command):
        """Internal helper to get response from tiers."""
        # --- TIER 1/2: Local Intent Matching (Static + Parametric) ---
        exec_str = skill_manager.get_intent_match(command)
        if exec_str:
            print(f"System: Intent Match found for '{exec_str}'")
            return skill_manager.execute(exec_str)

        # --- TIER 3: LLM Fallback (Reasoning/Extraction) ---
        if self.llm_ready:
            llm_response = self._call_llm(command)
            
            # Extract JSON from LLM response
            try:
                # Clean response (sometimes LLMs wrap in ```json)
                json_str = llm_response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                
                data = json.loads(json_str)
                intent = data.get("intent")
                args = data.get("arguments", {})
                confidence = data.get("confidence", 0)

                if intent and confidence > 0.7:
                    # Construct execution string: tool_name("arg1", "arg2")
                    arg_vals = [f"\"{v}\"" if isinstance(v, str) else str(v) for v in args.values()]
                    exec_str = f"{intent}({', '.join(arg_vals)})"
                    print(f"System: LLM Intent Match ({intent}) with {int(confidence*100)}% confidence.")
                    return skill_manager.execute(exec_str)
                
                return data.get("natural_response", "I understood that, but I'm not sure how to help yet.")
            except Exception as e:
                print(f"System: LLM Response failed JSON parsing: {e}")
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
            elif self.llm_provider == "ollama":
                import ollama
                # We reuse self.messages (containing system prompt) for KV-caching benefits in Ollama/llama.cpp
                # For pure intent extraction, we don't want history to bleed in, 
                # so we only send [System, CurrentUserMessage]
                messages = self.messages + [{"role": "user", "content": command}]
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    format="json",
                    options={
                        "temperature": 0.2, # Low temp for deterministic JSON
                        "num_predict": 256, # Limit response length to save time
                    }
                )
                return response['message']['content']
        except Exception as e:
            return f"Thinking error: {e}"

brain = Brain()
