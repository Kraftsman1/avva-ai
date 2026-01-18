"""
LM Studio Brain - Local LLM provider using LM Studio's OpenAI-compatible API.

LM Studio provides a local OpenAI-compatible server for running models locally.
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


class LMStudioBrain(BaseBrain):
    """
    Brain provider for LM Studio local server.
    
    Uses OpenAI-compatible API but runs fully locally.
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self.endpoint = config.config_data.get("endpoint", "http://localhost:1234/v1")
        self.model = config.config_data.get("model", "local-model")
        self.temperature = config.config_data.get("temperature", 0.2)
        self.max_tokens = config.config_data.get("max_tokens", 256)
        
        # Initialize client
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI-compatible client for LM Studio."""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.endpoint,
                api_key="lm-studio"  # LM Studio doesn't require real API key
            )
        except ImportError:
            pass
        except Exception as e:
            print(f"Error initializing LM Studio Brain: {e}")
    
    def get_capabilities(self) -> List[BrainCapability]:
        """LM Studio capabilities."""
        return [
            BrainCapability.CHAT,
            BrainCapability.JSON_MODE,
            BrainCapability.OFFLINE,
            BrainCapability.STREAMING
        ]
    
    def get_privacy_level(self) -> PrivacyLevel:
        """LM Studio is fully local."""
        return PrivacyLevel.LOCAL
    
    def health_check(self) -> BrainHealth:
        """Check LM Studio server availability."""
        try:
            from openai import OpenAI
            
            if not self.client:
                self._init_client()
            
            # Try to list models
            import time
            start = time.time()
            
            models = self.client.models.list()
            available_models = [model.id for model in models.data]
            
            latency = (time.time() - start) * 1000
            
            if not available_models:
                return BrainHealth(
                    status=BrainStatus.MISCONFIGURED,
                    message="LM Studio server running but no models loaded",
                    available_models=[]
                )
            
            return BrainHealth(
                status=BrainStatus.AVAILABLE,
                message=f"LM Studio ready with {len(available_models)} model(s)",
                available_models=available_models,
                latency_ms=latency
            )
            
        except ImportError:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="OpenAI package not installed. Run: pip install openai"
            )
        except Exception as e:
            return BrainHealth(
                status=BrainStatus.UNREACHABLE,
                message=f"Cannot connect to LM Studio at {self.endpoint}: {str(e)}"
            )
    
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """Execute reasoning with LM Studio."""
        try:
            if not self.client:
                self._init_client()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context, constraints)
            
            # Execute
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            try:
                # Clean response
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
                return self._build_success_response(
                    content=content,
                    confidence=0.5,
                    natural_response=content
                )
                
        except Exception as e:
            return self._build_error_response(f"LM Studio error: {str(e)}")
    
    def _build_system_prompt(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Build system prompt for LM Studio."""
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
