"""
Brain Manager - Central registry and orchestrator for all Brain providers.

This module manages Brain registration, selection, and fallback logic.
"""

from typing import Dict, List, Optional, Any
from core.brain_interface import Brain, BrainCapability, BrainConfig, BrainHealth, BrainResponse, PrivacyLevel
from core.persistence import storage
import json


class BrainManager:
    """
    Manages all registered Brain providers and handles Brain selection logic.
    """
    
    def __init__(self):
        self.registry: Dict[str, Brain] = {}  # brain_id -> Brain instance
        self.active_brain_id: Optional[str] = None
        self.fallback_brain_id: Optional[str] = None
        self.rules_only_mode: bool = False
        self.auto_selection_enabled: bool = True
        
    def register_brain(self, brain: Brain) -> None:
        """
        Register a Brain provider.
        
        Args:
            brain: Brain instance to register
        """
        self.registry[brain.id] = brain
        print(f"🧠 Registered Brain: {brain.name} ({brain.provider})")
        
        # Set as active if marked in config
        if brain.config.is_active:
            self.active_brain_id = brain.id
        
        # Set as fallback if marked in config
        if brain.config.is_fallback:
            self.fallback_brain_id = brain.id
    
    def unregister_brain(self, brain_id: str) -> bool:
        """
        Unregister a Brain provider.
        
        Args:
            brain_id: ID of Brain to unregister
            
        Returns:
            True if successful, False if not found
        """
        if brain_id in self.registry:
            del self.registry[brain_id]
            
            # Clear active/fallback if this was the selected Brain
            if self.active_brain_id == brain_id:
                self.active_brain_id = None
            if self.fallback_brain_id == brain_id:
                self.fallback_brain_id = None
            
            return True
        return False
    
    def get_brain(self, brain_id: str) -> Optional[Brain]:
        """
        Get a Brain by ID.
        
        Args:
            brain_id: Brain identifier
            
        Returns:
            Brain instance or None if not found
        """
        return self.registry.get(brain_id)
    
    def get_active_brain(self) -> Optional[Brain]:
        """
        Get the currently active Brain.
        
        Returns:
            Active Brain instance or None
        """
        if self.rules_only_mode:
            return self.get_brain("rules")
        
        if self.active_brain_id:
            return self.registry.get(self.active_brain_id)
        
        return None
    
    def set_active_brain(self, brain_id: str) -> bool:
        """
        Set the active Brain.
        
        Args:
            brain_id: ID of Brain to activate
            
        Returns:
            True if successful, False if Brain not found
        """
        if brain_id in self.registry:
            # Update old active Brain config
            if self.active_brain_id:
                old_brain = self.registry[self.active_brain_id]
                old_brain.config.is_active = False
            
            # Set new active Brain
            self.active_brain_id = brain_id
            new_brain = self.registry[brain_id]
            new_brain.config.is_active = True
            
            # Persist to database
            storage.set_active_brain(brain_id)
            
            print(f"🧠 Active Brain set to: {new_brain.name}")
            return True
        
        return False
    
    def set_fallback_brain(self, brain_id: str) -> bool:
        """
        Set the fallback Brain.
        
        Args:
            brain_id: ID of Brain to use as fallback
            
        Returns:
            True if successful, False if Brain not found
        """
        if brain_id in self.registry:
            # Update old fallback Brain config
            if self.fallback_brain_id:
                old_brain = self.registry[self.fallback_brain_id]
                old_brain.config.is_fallback = False
            
            # Set new fallback Brain
            self.fallback_brain_id = brain_id
            new_brain = self.registry[brain_id]
            new_brain.config.is_fallback = True
            
            # Persist to database
            storage.set_fallback_brain(brain_id)
            
            print(f"🧠 Fallback Brain set to: {new_brain.name}")
            return True
        
        return False
    
    def select_brain(self, context: Optional[Dict] = None) -> Optional[Brain]:
        """
        Select appropriate Brain based on context and settings.
        
        Args:
            context: Request context for intelligent selection
            
        Returns:
            Selected Brain instance or None
        """
        # Rules-only mode override
        if self.rules_only_mode:
            return self.get_brain("rules")
        
        # Auto-selection based on context
        if self.auto_selection_enabled and context:
            brain = self._auto_select_brain(context)
            if brain:
                return brain
        
        # Default to active Brain
        active = self.get_active_brain()
        if active:
            # Health check
            health = active.get_cached_health() if hasattr(active, 'get_cached_health') else active.health_check()
            if health.status.value == "available":
                return active
            
            # Active Brain unhealthy, try fallback
            print(f"⚠️ Active Brain '{active.name}' is {health.status.value}: {health.message}")
            return self._try_fallback(f"Primary Brain unavailable")
        
        # No active Brain, try fallback
        return self._try_fallback("No active Brain configured")
    
    def _auto_select_brain(self, context: Dict) -> Optional[Brain]:
        """
        Automatically select Brain based on context analysis.
        
        Args:
            context: Request context
            
        Returns:
            Selected Brain or None
        """
        # Check for sensitivity markers
        is_sensitive = context.get("sensitive", False)
        requires_privacy = context.get("requires_privacy", False)
        
        # If sensitive, prefer local Brains
        if is_sensitive or requires_privacy:
            local_brains = self.get_brains_by_privacy_level(PrivacyLevel.LOCAL)
            for brain in local_brains:
                health = brain.health_check()
                if health.status.value == "available":
                    print(f"🔒 Auto-selected local Brain '{brain.name}' for sensitive request")
                    return brain
        
        # Check for required capabilities
        required_capability = context.get("required_capability")
        if required_capability:
            capable_brains = self.get_brains_by_capability(BrainCapability(required_capability))
            if capable_brains:
                return capable_brains[0]  # Return first capable Brain
        
        return None
    
    def _try_fallback(self, reason: str) -> Optional[Brain]:
        """
        Try to use fallback Brain.
        
        Args:
            reason: Reason for fallback
            
        Returns:
            Fallback Brain or None
        """
        if self.fallback_brain_id:
            fallback = self.registry.get(self.fallback_brain_id)
            if fallback:
                health = fallback.health_check()
                if health.status.value == "available":
                    print(f"🔄 Falling back to '{fallback.name}': {reason}")
                    return fallback
                else:
                    print(f"❌ Fallback Brain '{fallback.name}' also unavailable: {health.message}")
        
        return None
    
    def get_brains_by_capability(self, capability: BrainCapability) -> List[Brain]:
        """
        Get all Brains that support a specific capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of capable Brains
        """
        return [
            brain for brain in self.registry.values()
            if brain.supports_capability(capability)
        ]
    
    def get_brains_by_privacy_level(self, privacy_level: PrivacyLevel) -> List[Brain]:
        """
        Get all Brains at a specific privacy level.
        
        Args:
            privacy_level: Required privacy level
            
        Returns:
            List of matching Brains
        """
        return [
            brain for brain in self.registry.values()
            if brain.get_privacy_level() == privacy_level
        ]
    
    def get_all_brains(self) -> List[Brain]:
        """
        Get all registered Brains.
        
        Returns:
            List of all Brain instances
        """
        return list(self.registry.values())
    
    def get_brain_display_info(self) -> List[Dict]:
        """
        Get display information for all Brains (for UI).
        
        Returns:
            List of Brain display info dictionaries
        """
        return [brain.get_display_info() for brain in self.registry.values()]
    
    def update_brain_config(self, brain_id: str, config_data: Dict[str, Any]) -> bool:
        """
        Update the configuration of a specific Brain.
        
        Args:
            brain_id: ID of Brain to update
            config_data: New configuration dictionary
            
        Returns:
            True if successful, False if Brain not found
        """
        brain = self.get_brain(brain_id)
        if brain:
            success = brain.update_config(config_data)
            if success:
                # Persist to database
                storage.save_brain_config(
                    brain_id, 
                    brain.name, 
                    brain.provider, 
                    brain.get_privacy_level().value, 
                    brain.config.config_data, 
                    [c.value for c in brain.get_capabilities()]
                )
                print(f"🧠 Updated configuration for Brain: {brain.name}")
                return True
        return False
    
    def set_rules_only_mode(self, enabled: bool) -> None:
        """
        Enable or disable rules-only mode (no LLM).
        
        Args:
            enabled: True to enable rules-only mode
        """
        self.rules_only_mode = enabled
        storage.save_config("RULES_ONLY_MODE", enabled)
        
        if enabled:
            print("🔒 Rules-only mode enabled - LLM Brains disabled")
        else:
            print("🧠 Rules-only mode disabled - LLM Brains enabled")
    
    def set_auto_selection(self, enabled: bool) -> None:
        """
        Enable or disable automatic Brain selection.
        
        Args:
            enabled: True to enable auto-selection
        """
        self.auto_selection_enabled = enabled
        storage.save_config("AUTO_BRAIN_SELECTION", enabled)


# Global instance
brain_manager = BrainManager()
