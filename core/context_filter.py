"""
Context filtering and redaction for privacy-aware Brain execution.

This module handles context minimization and sensitive data redaction
based on Brain privacy levels.
"""

import re
from pathlib import Path
from typing import Dict, Any
from core.brain_interface import PrivacyLevel


class ContextFilter:
    """
    Filters and redacts context based on Brain privacy level.
    """
    
    @staticmethod
    def filter_for_privacy_level(context: Dict[str, Any], privacy_level: PrivacyLevel, filter_level: str = "auto") -> Dict[str, Any]:
        """
        Filter context based on privacy level.
        
        Args:
            context: Original context dictionary
            privacy_level: Brain's privacy level
            filter_level: Filter aggressiveness (auto, minimal, moderate, aggressive, none)
            
        Returns:
            Filtered context dictionary
        """
        if filter_level == "none":
            return context
        
        # Determine actual filter level
        if filter_level == "auto":
            if privacy_level == PrivacyLevel.LOCAL:
                actual_level = "minimal"
            elif privacy_level == PrivacyLevel.TRUSTED_CLOUD:
                actual_level = "moderate"
            else:  # EXTERNAL_CLOUD
                actual_level = "aggressive"
        else:
            actual_level = filter_level
        
        # Apply filtering
        if actual_level == "minimal":
            return ContextFilter._minimal_filter(context)
        elif actual_level == "moderate":
            return ContextFilter._moderate_filter(context)
        elif actual_level == "aggressive":
            return ContextFilter._aggressive_filter(context)
        
        return context
    
    @staticmethod
    def _minimal_filter(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Minimal filtering - only remove obviously sensitive data.
        
        Args:
            context: Original context
            
        Returns:
            Filtered context
        """
        filtered = context.copy()
        
        # Remove API keys and tokens
        if "api_keys" in filtered:
            del filtered["api_keys"]
        if "tokens" in filtered:
            del filtered["tokens"]
        
        return filtered
    
    @staticmethod
    def _moderate_filter(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Moderate filtering - redact paths and system identifiers.
        
        Args:
            context: Original context
            
        Returns:
            Filtered context
        """
        filtered = ContextFilter._minimal_filter(context)
        
        # Redact absolute paths
        for key, value in filtered.items():
            if isinstance(value, str):
                filtered[key] = ContextFilter._redact_paths(value)
        
        # Remove system identifiers
        if "hostname" in filtered:
            filtered["hostname"] = "[REDACTED]"
        if "username" in filtered:
            filtered["username"] = "[USER]"
        if "home_dir" in filtered:
            filtered["home_dir"] = "~"
        
        return filtered
    
    @staticmethod
    def _aggressive_filter(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggressive filtering - only keep user's explicit query.
        
        Args:
            context: Original context
            
        Returns:
            Minimal context with only query
        """
        # Only preserve the user's query
        return {
            "query": context.get("query", ""),
            "privacy_note": "Context minimized for external cloud provider"
        }
    
    @staticmethod
    def _redact_paths(text: str) -> str:
        """
        Redact absolute file paths in text.
        
        Args:
            text: Text potentially containing paths
            
        Returns:
            Text with paths redacted
        """
        # Replace absolute paths with relative or generic markers
        # Match /home/username/... or /path/to/...
        text = re.sub(r'/home/[^/\s]+', '~', text)
        text = re.sub(r'/[a-zA-Z0-9_\-./]+', '[PATH]', text)
        
        return text
    
    @staticmethod
    def redact_sensitive_data(text: str) -> str:
        """
        Redact common sensitive patterns from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        # Email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # IP addresses
        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]', text)
        
        # API keys (common patterns)
        text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[KEY]', text)
        
        # UUIDs
        text = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '[UUID]', text)
        
        return text
