"""
OpenAI Brain - Cloud LLM provider using OpenAI's API.
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


class OpenAIBrain(BaseBrain):
    """
    Brain provider for OpenAI API (GPT models).
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self.api_key = config.config_data.get("api_key", "")
        self.model = config.config_data.get("model", "gpt-4o-mini")
        self.temperature = config.config_data.get("temperature", 0.2)
        
        # Initialize client
        self.client = None
        if self.api_key:
            self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            pass
        except Exception as e:
            print(f"Error initializing OpenAI Brain: {e}")
    
    def get_capabilities(self) -> List[BrainCapability]:
        """OpenAI capabilities."""
        capabilities = [
            BrainCapability.CHAT,
            BrainCapability.TOOL_CALLING,
            BrainCapability.JSON_MODE,
            BrainCapability.STREAMING
        ]
        
        # Vision support for GPT-4 Vision and GPT-4o models
        if "vision" in self.model.lower() or "gpt-4o" in self.model.lower():
            capabilities.append(BrainCapability.VISION)
        
        return capabilities
    
    def get_privacy_level(self) -> PrivacyLevel:
        """OpenAI is an external cloud provider."""
        return PrivacyLevel.EXTERNAL_CLOUD
    
    def health_check(self) -> BrainHealth:
        """Check OpenAI API availability."""
        if not self.api_key:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="API key not configured"
            )
        
        try:
            from openai import OpenAI
            
            if not self.client:
                self._init_client()
            
            # Try a minimal request
            import time
            start = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            latency = (time.time() - start) * 1000
            
            return BrainHealth(
                status=BrainStatus.AVAILABLE,
                message=f"OpenAI ready with model '{self.model}'",
                latency_ms=latency
            )
            
        except ImportError:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="OpenAI package not installed. Run: pip install openai"
            )
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return BrainHealth(
                    status=BrainStatus.MISCONFIGURED,
                    message=f"Invalid API key: {error_msg}"
                )
            return BrainHealth(
                status=BrainStatus.UNREACHABLE,
                message=f"Cannot connect to OpenAI: {error_msg}"
            )
    
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """Execute reasoning with OpenAI."""
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
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Parse JSON
            try:
                data = json.loads(content)
                intent = data.get("intent")
                arguments = data.get("arguments", {})
                confidence = data.get("confidence", 0.0)
                natural_response = data.get("natural_response")
                
                # Estimate cost
                cost = self._calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
                
                return self._build_success_response(
                    content=content,
                    confidence=confidence,
                    intent=intent,
                    arguments=arguments,
                    natural_response=natural_response,
                    tokens_used=tokens_used,
                    cost_usd=cost
                )
            except json.JSONDecodeError:
                return self._build_success_response(
                    content=content,
                    confidence=0.5,
                    natural_response=content,
                    tokens_used=tokens_used
                )
                
        except Exception as e:
            return self._build_error_response(f"OpenAI error: {str(e)}")
    
    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost for OpenAI."""
        # Rough token estimation (4 chars ≈ 1 token)
        estimated_input_tokens = len(prompt) // 4
        estimated_output_tokens = estimated_input_tokens * 2  # Assume 2:1 ratio
        
        return self._calculate_cost(estimated_input_tokens, estimated_output_tokens)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost based on model pricing."""
        # GPT-4o-mini pricing (as of 2024)
        if "gpt-4o-mini" in self.model:
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
        # GPT-4o pricing
        elif "gpt-4o" in self.model:
            input_cost = (input_tokens / 1_000_000) * 2.50
            output_cost = (output_tokens / 1_000_000) * 10.00
        # GPT-4 Turbo pricing
        elif "gpt-4-turbo" in self.model:
            input_cost = (input_tokens / 1_000_000) * 10.00
            output_cost = (output_tokens / 1_000_000) * 30.00
        # Default fallback
        else:
            input_cost = (input_tokens / 1_000_000) * 1.00
            output_cost = (output_tokens / 1_000_000) * 2.00
        
        return input_cost + output_cost
    
    def _build_system_prompt(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Build system prompt for OpenAI."""
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
