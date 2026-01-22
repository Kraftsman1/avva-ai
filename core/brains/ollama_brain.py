"""
Ollama Brain - Local LLM provider using Ollama.

Supports fully offline operation with local models.
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


class OllamaBrain(BaseBrain):
    """
    Brain provider for Ollama local LLM backend.
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self.host = config.config_data.get("host", "http://localhost:11434")
        self.model = config.config_data.get("model", "llama3")
        self.temperature = config.config_data.get("temperature", 0.2)
        self.max_tokens = config.config_data.get("max_tokens", 256)
        
        # Detect capabilities based on model
        self._detect_capabilities()
    
    def _detect_capabilities(self):
        """Detect model capabilities."""
        self.capabilities = [
            BrainCapability.CHAT,
            BrainCapability.JSON_MODE,
            BrainCapability.OFFLINE
        ]
        
        # Check for vision support (llava, bakllava models)
        if "llava" in self.model.lower() or "vision" in self.model.lower():
            self.capabilities.append(BrainCapability.VISION)
    
    def get_capabilities(self) -> List[BrainCapability]:
        """Return Ollama capabilities."""
        return self.capabilities
    
    def get_privacy_level(self) -> PrivacyLevel:
        """Ollama is fully local."""
        return PrivacyLevel.LOCAL
    
    def health_check(self) -> BrainHealth:
        """Check Ollama server and model availability."""
        try:
            import ollama
            
            # Try to list models
            models_response = ollama.list()
            # Handle different response formats (newer ollama-python versions return an object)
            if hasattr(models_response, 'models'):
                models = models_response.models
                available_models = [m.model for m in models] if hasattr(models[0], 'model') else [m.name for m in models]
            else:
                available_models = [model['name'] for model in models_response.get('models', [])]
            
            if not available_models:
                return BrainHealth(
                    status=BrainStatus.MISCONFIGURED,
                    message="Ollama server running but no models found. Run 'ollama pull llama3' in terminal.",
                    available_models=[]
                )

            # Check if configured model is available (exact match)
            if self.model in available_models:
                import time
                start = time.time()
                try:
                    ollama.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": "test"}],
                        options={"num_predict": 1}
                    )
                    latency = (time.time() - start) * 1000
                    return BrainHealth(
                        status=BrainStatus.AVAILABLE,
                        message=f"Ollama ready with model '{self.model}'",
                        available_models=available_models,
                        latency_ms=latency
                    )
                except Exception as e:
                    # If listing worked but chat failed (e.g., OOM), we still consider the provider AVAILABLE
                    # so the user can switch capabilities or models in the UI.
                    error_msg = str(e)
                    if "memory" in error_msg.lower():
                        msg = f"Ollama connected, but '{self.model}' is too large for your RAM. Please select a smaller model."
                    else:
                        msg = f"Ollama connected, but inference failed: {error_msg}"
                        
                    return BrainHealth(
                        status=BrainStatus.AVAILABLE,
                        message=msg,
                        available_models=available_models
                    )
            
            # Fuzzy match or suggest
            suggestions = [m for m in available_models if self.model.lower() in m.lower()]
            best_match = suggestions[0] if suggestions else available_models[0]
            
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message=f"Model '{self.model}' not found. Did you mean '{best_match}'? Select from dropdown below.",
                available_models=available_models
            )
            
        except ImportError:
            return BrainHealth(
                status=BrainStatus.MISCONFIGURED,
                message="Ollama Python package not installed. Run: pip install ollama"
            )
        except Exception as e:
            return BrainHealth(
                status=BrainStatus.UNREACHABLE,
                message=f"Cannot connect to Ollama at {self.host}: {str(e)}"
            )
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update Ollama specific config."""
        self.host = config_data.get("host", self.host)
        self.model = config_data.get("model", self.model)
        self.temperature = config_data.get("temperature", self.temperature)
        self.max_tokens = config_data.get("max_tokens", self.max_tokens)
        
        # Update underlying config object
        return super().update_config(config_data)

    def get_config_schema(self) -> List[Dict[str, Any]]:
        """Return schema for Ollama settings."""
        return [
            {
                "name": "host",
                "type": "string",
                "description": "Ollama API Endpoint",
                "default": "http://localhost:11434"
            },
            {
                "name": "model",
                "type": "string",
                "description": "Neural Weights (Llama3, Mistral, etc)",
                "default": "llama3:8b"
            },
            {
                "name": "temperature",
                "type": "float",
                "description": "Creativity vs Precision",
                "default": "0.7",
                "min": 0,
                "max": 1,
                "step": 0.05
            },
            {
                "name": "max_tokens",
                "type": "int",
                "description": "Maximum Neural output buffer",
                "default": "4096",
                "min": 256,
                "max": 32768
            }
        ]

    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """Execute reasoning with Ollama."""
        try:
            import ollama
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context, constraints)
            
            # Execute
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = ollama.chat(
                model=self.model,
                messages=messages,
                format="json",
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            # Parse response
            content = response['message']['content']
            
            # Try to parse JSON
            try:
                data = json.loads(content)
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
            return self._build_error_response(f"Ollama execution error: {str(e)}")
    
    def _build_system_prompt(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Build system prompt for Ollama."""
        # Import here to avoid circular dependency
        from core.skill_manager import skill_manager
        
        prompt = (
            f"You are an intelligent Linux Virtual Assistant. "
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
