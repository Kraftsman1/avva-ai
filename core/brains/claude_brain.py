"""
Claude Brain - Cloud LLM provider using Anthropic's Claude API.
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


class ClaudeBrain(BaseBrain):
    """
    Brain provider for Anthropic Claude API.
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self.api_key = config.config_data.get("api_key", "")
        self.model = config.config_data.get("model", "claude-3-5-sonnet-20241022")
        self.temperature = config.config_data.get("temperature", 0.2)
        self.max_tokens = config.config_data.get("max_tokens", 1024)
        
        # Initialize client
        self.client = None
        if self.api_key:
            self._init_client()
    
    def _init_client(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            pass
        except Exception as e:
            print(f"Error initializing Claude Brain: {e}")
    
    def get_capabilities(self) -> List[BrainCapability]:
        """Claude capabilities."""
        capabilities = [
            BrainCapability.CHAT,
            BrainCapability.TOOL_CALLING,
            BrainCapability.STREAMING
        ]
        
        # Vision support for Claude 3+ models
        if "claude-3" in self.model.lower():
            capabilities.append(BrainCapability.VISION)
        
        return capabilities
    
    def get_privacy_level(self) -> PrivacyLevel:
        """Claude/Anthropic is an external cloud provider."""
        return PrivacyLevel.EXTERNAL_CLOUD
    
    def health_check(self) -> BrainHealth:
        """Check Claude API availability."""
        if not self.api_key:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="API key not configured"
            )
        
        try:
            from anthropic import Anthropic
            
            if not self.client:
                self._init_client()
            
            # Try a minimal request
            import time
            start = time.time()
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            latency = (time.time() - start) * 1000
            
            return BrainHealth(
                status=BrainStatus.AVAILABLE,
                message=f"Claude ready with model '{self.model}'",
                latency_ms=latency
            )
            
        except ImportError:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="Anthropic package not installed. Run: pip install anthropic"
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
                message=f"Cannot connect to Claude: {error_msg}"
            )
    
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """Execute reasoning with Claude."""
        try:
            if not self.client:
                self._init_client()
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context, constraints)
            
            # Execute
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
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
                
                # Calculate cost
                cost = self._calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
                
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
            return self._build_error_response(f"Claude error: {str(e)}")
    
    def estimate_cost(self, prompt: str) -> float:
        """Estimate cost for Claude."""
        # Rough token estimation (4 chars ≈ 1 token)
        estimated_input_tokens = len(prompt) // 4
        estimated_output_tokens = estimated_input_tokens * 2
        
        return self._calculate_cost(estimated_input_tokens, estimated_output_tokens)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost based on model pricing."""
        # Claude 3.5 Sonnet pricing (as of 2024)
        if "claude-3-5-sonnet" in self.model or "claude-3.5-sonnet" in self.model:
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00
        # Claude 3 Opus pricing
        elif "claude-3-opus" in self.model:
            input_cost = (input_tokens / 1_000_000) * 15.00
            output_cost = (output_tokens / 1_000_000) * 75.00
        # Claude 3 Haiku pricing
        elif "claude-3-haiku" in self.model:
            input_cost = (input_tokens / 1_000_000) * 0.25
            output_cost = (output_tokens / 1_000_000) * 1.25
        # Default fallback
        else:
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00
        
        return input_cost + output_cost
    
    def _build_system_prompt(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Build system prompt for Claude."""
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
