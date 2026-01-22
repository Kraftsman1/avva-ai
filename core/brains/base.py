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
from typing import List, Dict, Any
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
