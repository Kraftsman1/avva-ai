"""
Brain Interface and Base Classes for AVA's Configurable LLM System.

This module defines the abstract interface that all Brain providers must implement,
along with supporting enums and data classes for capabilities, privacy levels, and responses.
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


class BrainCapability(Enum):
    """Capabilities that a Brain provider may support."""
    CHAT = "chat"                    # Free-form conversational reasoning
    TOOL_CALLING = "tool_calling"    # Structured function calling
    JSON_MODE = "json_mode"          # Guaranteed structured JSON output
    STREAMING = "streaming"          # Token-by-token streaming
    VISION = "vision"                # Image input processing
    OFFLINE = "offline"              # No network required


class PrivacyLevel(Enum):
    """Privacy classification for Brain providers."""
    LOCAL = "local"                          # Fully local, no network
    TRUSTED_CLOUD = "trusted_cloud"          # First-party cloud (Google, OpenAI official)
    EXTERNAL_CLOUD = "external_cloud"        # Third-party cloud services


class BrainStatus(Enum):
    """Health status of a Brain provider."""
    AVAILABLE = "available"          # Ready to use
    UNREACHABLE = "unreachable"      # Cannot connect
    MISCONFIGURED = "misconfigured"  # Configuration error
    DEGRADED = "degraded"            # Partially functional


@dataclass
class BrainHealth:
    """Health check result for a Brain provider."""
    status: BrainStatus
    message: str
    available_models: Optional[List[str]] = None
    latency_ms: Optional[float] = None
    last_checked: datetime = None
    
    def __post_init__(self):
        if self.last_checked is None:
            self.last_checked = datetime.now()


@dataclass
class BrainResponse:
    """Standardized response from a Brain execution."""
    success: bool
    content: str
    confidence: float = 0.0
    intent: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    natural_response: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    error: Optional[str] = None


@dataclass
class BrainConfig:
    """Configuration for a Brain instance."""
    id: str
    name: str
    provider: str
    config_data: Dict[str, Any]
    is_active: bool = False
    is_fallback: bool = False
    context_filter_enabled: bool = True
    context_filter_level: str = "auto"  # auto, minimal, moderate, aggressive, none


class Brain(ABC):
    """
    Abstract base class for all Brain providers.
    
    All LLM backends must implement this interface to be compatible with AVA.
    """
    
    def __init__(self, config: BrainConfig):
        """
        Initialize the Brain with configuration.
        
        Args:
            config: BrainConfig instance with provider-specific settings
        """
        self.config = config
        self.id = config.id
        self.name = config.name
        self.provider = config.provider
        
    @abstractmethod
    def get_capabilities(self) -> List[BrainCapability]:
        """
        Return the list of capabilities this Brain supports.
        
        Returns:
            List of BrainCapability enums
        """
        pass
    
    @abstractmethod
    def get_privacy_level(self) -> PrivacyLevel:
        """
        Return the privacy level of this Brain.
        
        Returns:
            PrivacyLevel enum indicating data handling
        """
        pass
    
    @abstractmethod
    def health_check(self) -> BrainHealth:
        """
        Perform a health check on the Brain provider.
        
        Should verify:
        - Connection to backend (if applicable)
        - Model availability
        - Configuration validity
        
        Returns:
            BrainHealth object with status and details
        """
        pass
    
    @abstractmethod
    def execute(self, prompt: str, context: Dict[str, Any], constraints: Dict[str, Any]) -> BrainResponse:
        """
        Execute a reasoning task with the Brain.
        
        Args:
            prompt: User's input/query
            context: Additional context (filtered based on privacy level)
            constraints: Execution constraints (JSON schema, tools, etc.)
        
        Returns:
            BrainResponse with results or error
        """
        pass
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Update the Brain's provider-specific configuration.
        
        Args:
            config_data: Dictionary of new settings
            
        Returns:
            True if applied successfully, False otherwise
        """
        self.config.config_data.update(config_data)
        return True
    
    def get_config_schema(self) -> List[Dict[str, Any]]:
        """
        Return the configuration schema for this Brain provider.
        
        Used by the UI to render configuration forms.
        
        Returns:
            List of dictionaries describing config fields:
            [{"name": "field_name", "type": "string|int|float|bool", "description": "...", "default": "..."}]
        """
        return []
    
    def estimate_cost(self, prompt: str) -> Optional[float]:
        """
        Estimate the cost in USD for processing this prompt.
        
        Optional method - only relevant for paid cloud providers.
        
        Args:
            prompt: The prompt to estimate cost for
            
        Returns:
            Estimated cost in USD, or None if not applicable
        """
        return None
    
    def supports_capability(self, capability: BrainCapability) -> bool:
        """
        Check if this Brain supports a specific capability.
        
        Args:
            capability: BrainCapability to check
            
        Returns:
            True if supported, False otherwise
        """
        return capability in self.get_capabilities()
    
    def get_display_info(self) -> Dict[str, Any]:
        """
        Get display information for UI rendering.
        
        Returns:
            Dictionary with display metadata
        """
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "privacy_level": self.get_privacy_level().value,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "is_active": self.config.is_active,
            "is_fallback": self.config.is_fallback,
            "config_data": self.config.config_data,
            "config_schema": self.get_config_schema(),
            "health": {
                "status": "available",
                "message": "Protocol ready",
                "available_models": []
            }
        }
