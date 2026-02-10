"""
Base Brain class with common functionality for all Brain providers.
"""

from core.brain_interface import (
    Brain,
    BrainCapability,
    BrainConfig,
    BrainHealth,
    BrainResponse,
    BrainStatus,
    PrivacyLevel
)
from typing import List, Dict, Any, Optional
import json
import time


class BaseBrain(Brain):
    """
    Base implementation of Brain with common utilities.
    
    Concrete Brain providers should inherit from this class.
    """
    
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        self._last_health_check = None
        self._health_cache_seconds = 30  # Cache health checks for 30 seconds
    
    def get_cached_health(self) -> BrainHealth:
        """
        Get cached health check result if recent, otherwise perform new check.
        
        Returns:
            BrainHealth object
        """
        if self._last_health_check is None:
            self._last_health_check = self.health_check()
            return self._last_health_check
        
        # Check if cache is still valid
        age = (time.time() - self._last_health_check.last_checked.timestamp())
        if age < self._health_cache_seconds:
            return self._last_health_check
        
        # Cache expired, perform new check
        self._last_health_check = self.health_check()
        return self._last_health_check
    
    def _build_error_response(self, error_message: str) -> BrainResponse:
        """
        Helper to build standardized error responses.
        
        Args:
            error_message: Error description
            
        Returns:
            BrainResponse with error
        """
        return BrainResponse(
            success=False,
            content="",
            error=error_message
        )
    
    def _build_success_response(
        self,
        content: str,
        confidence: float = 0.0,
        intent: str = None,
        arguments: Dict[str, Any] = None,
        natural_response: str = None,
        tokens_used: int = None,
        cost_usd: float = None
    ) -> BrainResponse:
        """
        Helper to build standardized success responses.
        
        Args:
            content: Response content
            confidence: Confidence score (0.0-1.0)
            intent: Extracted intent/tool name
            arguments: Intent arguments
            natural_response: Human-readable response
            tokens_used: Token count
            cost_usd: Cost in USD
            
        Returns:
            BrainResponse with success
        """
        return BrainResponse(
            success=True,
            content=content,
            confidence=confidence,
            intent=intent,
            arguments=arguments,
            natural_response=natural_response,
            tokens_used=tokens_used,
            cost_usd=cost_usd
        )

    def _build_workflow_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build the workflow planning prompt shared across all providers."""
        available_skills = context.get("available_skills", {})
        skills_list = "\n".join(
            f"  - \"{phrase}\"" for phrase in list(available_skills.keys())[:20]
        ) or "  (none registered)"

        return (
            "You are a task planning assistant. Break the following user request into "
            "clear sequential steps. Each step should be atomic and independently executable.\n\n"
            f"User Request: {request}\n\n"
            f"Available skill phrases (can be used as 'intent' for direct execution):\n"
            f"{skills_list}\n\n"
            "Respond ONLY with a valid JSON object using this exact structure:\n"
            "{\n"
            '  "title": "Short workflow title (5 words max)",\n'
            '  "description": "One sentence describing what this workflow does",\n'
            '  "steps": [\n'
            "    {\n"
            '      "id": "step_1",\n'
            '      "description": "Short human-readable step name",\n'
            '      "action": "Detailed instruction for what to do in this step",\n'
            '      "intent": "matching skill phrase or null",\n'
            '      "arguments": {},\n'
            '      "dependencies": []\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "RULES:\n"
            "1. Only include 'intent' if it exactly matches one of the available skill phrases.\n"
            "2. 'dependencies' must list step IDs that must complete before this step.\n"
            "3. Keep steps between 2 and 6 total.\n"
            "4. Output ONLY the JSON object. No extra text."
        )

    def _parse_workflow_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Parse and validate workflow JSON from model output."""
        try:
            text = raw.strip()
            # Strip code fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)

            # Validate required fields
            if not isinstance(data.get("steps"), list) or len(data["steps"]) == 0:
                return None

            # Ensure each step has required fields
            for i, step in enumerate(data["steps"]):
                step.setdefault("id", f"step_{i + 1}")
                step.setdefault("description", f"Step {i + 1}")
                step.setdefault("action", step.get("description", ""))
                step.setdefault("intent", None)
                step.setdefault("arguments", {})
                step.setdefault("dependencies", [])

            return data

        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def get_display_info(self) -> Dict[str, Any]:
        """
        Get display information including cached health metadata.
        """
        info = super().get_display_info()
        health = self.get_cached_health()
        
        info["health"] = {
            "status": health.status.value,
            "message": health.message,
            "available_models": health.available_models or [],
            "latency_ms": health.latency_ms,
            "last_checked": health.last_checked.isoformat() if health.last_checked else None
        }
        
        return info
