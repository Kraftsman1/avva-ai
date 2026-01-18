"""
Rules Brain - Fallback Brain using deterministic rules and local intent matching.

This Brain works without any LLM and serves as the ultimate fallback.
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


class RulesBrain(BaseBrain):
    """
    Deterministic rules-based Brain that works without any LLM.
    
    Uses existing skill_manager intent matching and simple keyword extraction.
    """
    
    def __init__(self, config: BrainConfig = None):
        if config is None:
            config = BrainConfig(
                id="rules",
                name="Rules Engine",
                provider="local",
                config_data={}
            )
        super().__init__(config)
    
    def get_capabilities(self) -> List[BrainCapability]:
        """Rules Brain only supports offline operation."""
        return [BrainCapability.OFFLINE]
    
    def get_privacy_level(self) -> PrivacyLevel:
        """Fully local, no network required."""
        return PrivacyLevel.LOCAL
    
    def health_check(self) -> BrainHealth:
        """Rules Brain is always available."""
        return BrainHealth(
            status=BrainStatus.AVAILABLE,
            message="Rules engine ready (no LLM required)"
        )
    
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """
        Execute using deterministic rules and keyword matching.
        
        This is a simple fallback that doesn't use LLM reasoning.
        """
        # Import here to avoid circular dependency
        from core.skill_manager import skill_manager
        
        # Try to match using existing skill intent system
        exec_str = skill_manager.get_intent_match(prompt)
        
        if exec_str:
            # Found a match - return as intent
            # Parse tool name and arguments
            import re
            match = re.match(r"(\w+)\((.*)\)", exec_str)
            if match:
                tool_name = match.group(1)
                args_str = match.group(2)
                
                # Parse arguments
                arguments = {}
                if args_str:
                    args = [a.strip().strip('"').strip("'") for a in args_str.split(",")]
                    for i, arg in enumerate(args):
                        arguments[f"arg{i}"] = arg
                
                return self._build_success_response(
                    content=exec_str,
                    confidence=0.9,  # High confidence for exact matches
                    intent=tool_name,
                    arguments=arguments,
                    natural_response=f"Matched intent: {tool_name}"
                )
        
        # No match found - provide low-confidence conversational response
        return self._build_success_response(
            content="",
            confidence=0.0,
            natural_response=self._generate_fallback_response(prompt)
        )
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """
        Generate a simple fallback response for unmatched queries.
        
        Args:
            prompt: User's query
            
        Returns:
            Fallback response string
        """
        prompt_lower = prompt.lower()
        
        # Simple keyword-based responses
        if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm running in rules-only mode. I can help with basic tasks like telling time or launching apps."
        
        if any(word in prompt_lower for word in ["help", "what can you do"]):
            return "I'm in rules-only mode, so I can only handle specific commands. Try asking for the time, date, or to launch an application."
        
        if any(word in prompt_lower for word in ["thank", "thanks"]):
            return "You're welcome!"
        
        # Default fallback
        return "I couldn't find a direct match for that. I'm running in rules-only mode without LLM reasoning. Try a more specific command, or enable an LLM Brain in Settings."
