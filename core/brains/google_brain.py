"""
Google Gemini Brain - Cloud LLM provider using Google's Gemini API.
"""

from core.brains.base import BaseBrain
from core.brain_interface import (
    BrainCapability,
    BrainConfig,
    BrainHealth,
    BrainResponse,
    BrainStatus,
    PrivacyLevel
)
from typing import List, Dict, Any
import json


class GoogleBrain(BaseBrain):
    """
    Brain provider for Google Gemini API.
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self.api_key = config.config_data.get("api_key", "")
        self.model = config.config_data.get("model", "gemini-1.5-flash")
        self.temperature = config.config_data.get("temperature", 0.2)
        
        # Initialize client
        self.client = None
        self.chat = None
        if self.api_key:
            self._init_client()
    
    def _init_client(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            pass
        except Exception as e:
            print(f"Error initializing Google Brain: {e}")
    
    def get_capabilities(self) -> List[BrainCapability]:
        """Google Gemini capabilities."""
        capabilities = [
            BrainCapability.CHAT,
            BrainCapability.TOOL_CALLING,
            BrainCapability.JSON_MODE
        ]
        
        # Vision support for Gemini Pro Vision and 1.5+ models
        if "vision" in self.model.lower() or "1.5" in self.model or "2.0" in self.model:
            capabilities.append(BrainCapability.VISION)
        
        return capabilities
    
    def get_privacy_level(self) -> PrivacyLevel:
        """Google is a trusted first-party cloud provider."""
        return PrivacyLevel.TRUSTED_CLOUD
    
    def health_check(self) -> BrainHealth:
        """Check Google Gemini API availability."""
        if not self.api_key:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="API key not configured"
            )
        
        try:
            import google.generativeai as genai
            
            # Try a minimal request
            import time
            start = time.time()
            
            if not self.client:
                self._init_client()
            
            # Test with a minimal prompt
            response = self.client.generate_content("test")
            latency = (time.time() - start) * 1000
            
            return BrainHealth(
                status=BrainStatus.AVAILABLE,
                message=f"Google Gemini ready with model '{self.model}'",
                latency_ms=latency
            )
            
        except ImportError:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="Google Generative AI package not installed. Run: pip install google-generativeai"
            )
        except Exception as e:
            return BrainHealth(
                status=BrainStatus.UNREACHABLE,
                message=f"Cannot connect to Google Gemini: {str(e)}"
            )
    
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """Execute reasoning with Google Gemini."""
        try:
            if not self.client:
                self._init_client()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context, constraints)
            
            # Start chat if not exists
            if not self.chat:
                self.chat = self.client.start_chat(history=[])
                self.chat.send_message(system_prompt)
            
            # Send user message
            response = self.chat.send_message(prompt)
            content = response.text
            
            # Try to parse JSON
            try:
                # Clean response (sometimes wrapped in ```json)
                json_str = content.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                
                data = json.loads(json_str)
                intent = data.get("intent")
                arguments = data.get("arguments", {})
                confidence = data.get("confidence", 0.0)
                natural_response = data.get("natural_response")
                
                return self._build_success_response(
                    content=content,
                    confidence=confidence,
                    intent=intent,
                    arguments=arguments,
                    natural_response=natural_response
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._build_success_response(
                    content=content,
                    confidence=0.5,
                    natural_response=content
                )
                
        except Exception as e:
            return self._build_error_response(f"Google Gemini error: {str(e)}")
    
    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost for Google Gemini."""
        # Rough token estimation (4 chars ≈ 1 token)
        estimated_tokens = len(prompt) // 4
        
        # Gemini 1.5 Flash pricing (as of 2024)
        # Input: $0.075 per 1M tokens
        # Output: $0.30 per 1M tokens
        # Assume 2:1 output:input ratio
        input_cost = (estimated_tokens / 1_000_000) * 0.075
        output_cost = ((estimated_tokens * 2) / 1_000_000) * 0.30
        
        return input_cost + output_cost
    
    def _build_system_prompt(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Build system prompt for Google Gemini."""
        from core.skill_manager import skill_manager
        
        prompt = (
            "You are an intelligent Linux Virtual Assistant. "
            "Your goal is to extract intent and arguments from user commands. "
            "You MUST respond ONLY with a valid JSON object in the following format:\n"
            "{\n"
            '  "intent": "tool_name",\n'
            '  "arguments": {"param1": "value"},\n'
            '  "confidence": 0.95,\n'
            '  "natural_response": "Optional helpful message"\n'
            "}\n"
            "If no tool is appropriate, set intent to null and provide a conversational natural_response.\n"
            "Here are your currently installed tools:\n"
            f"{skill_manager.get_tool_descriptions()}\n\n"
            "STRICT RULES:\n"
            "1. Output ONLY JSON.\n"
            "2. Confidence must be between 0.0 and 1.0.\n"
            "3. If multiple tools fit, choose the best one."
        )
        
        return prompt
