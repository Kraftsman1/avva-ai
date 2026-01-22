"""
Brain - Facade for the new Brain Manager system.

This module maintains backward compatibility with the existing AVA codebase
while delegating to the new Brain Manager architecture.
"""

from core.brain_manager import brain_manager
from core.brain_interface import BrainConfig
from core.brains.rules_brain import RulesBrain
from core.brains.ollama_brain import OllamaBrain
from core.brains.google_brain import GoogleBrain
from core.brains.openai_brain import OpenAIBrain
from core.brains.claude_brain import ClaudeBrain
from core.brains.lmstudio_brain import LMStudioBrain
from core.context_filter import ContextFilter
from core.config import config
from core.persistence import storage
from core.skill_manager import skill_manager


class Brain:
    """
    Main Brain facade that orchestrates the new Brain Manager system.
    
    Maintains backward compatibility with existing AVA code while
    enabling the new pluggable Brain architecture.
    """
    
    def __init__(self):
        self.name = config.NAME
        self.manager = brain_manager
        
        # Initialize Brains
        self._initialize_brains()
        
        # Load active Brain from config
        self._load_active_brain()
    
    def _initialize_brains(self):
        """Auto-discover and register all available Brains."""
        print("🧠 Initializing Brain system...")
        
        # Always register Rules Brain (fallback)
        rules_brain = RulesBrain()
        self.manager.register_brain(rules_brain)
        
        # Load saved Brain configurations from database
        saved_brains = storage.load_brain_configs()
        
        if saved_brains:
            # Restore saved Brains
            for brain_data in saved_brains:
                self._restore_brain(brain_data)
        else:
            # First run - migrate from legacy config
            self._migrate_legacy_config()
            
        # Ensure LM Studio is registered if not already there
        if "lmstudio_default" not in self.manager.registry:
            self._register_default_lmstudio()
            
    def _register_default_lmstudio(self):
        """Register a default LM Studio brain."""
        brain_config = BrainConfig(
            id="lmstudio_default",
            name="LM Studio",
            provider="lmstudio",
            config_data={
                "endpoint": "http://localhost:1234/v1",
                "model": "local-model",
                "temperature": 0.2,
                "max_tokens": 1024
            },
            is_active=False,
            is_fallback=False
        )
        brain = LMStudioBrain(brain_config)
        self.manager.register_brain(brain)
        # Also persist it
        self._save_brain_to_db(brain)
    
    def _restore_brain(self, brain_data):
        """Restore a Brain from saved configuration."""
        try:
            brain_config = BrainConfig(
                id=brain_data['id'],
                name=brain_data['name'],
                provider=brain_data['provider'],
                config_data=brain_data['config_data'],
                is_active=brain_data['is_active'],
                is_fallback=brain_data['is_fallback']
            )
            
            # Create Brain instance based on provider
            if brain_data['provider'] == 'ollama':
                brain = OllamaBrain(brain_config)
            elif brain_data['provider'] == 'google':
                brain = GoogleBrain(brain_config)
            elif brain_data['provider'] == 'openai':
                brain = OpenAIBrain(brain_config)
            elif brain_data['provider'] == 'claude':
                brain = ClaudeBrain(brain_config)
            elif brain_data['provider'] == 'lmstudio':
                brain = LMStudioBrain(brain_config)
            else:
                print(f"⚠️ Unknown Brain provider: {brain_data['provider']}")
                return
            
            self.manager.register_brain(brain)
            
        except Exception as e:
            print(f"⚠️ Error restoring Brain '{brain_data['name']}': {e}")
    
    def _migrate_legacy_config(self):
        """Migrate from legacy config.py LLM settings to Brain system."""
        print("🔄 Migrating legacy LLM configuration to Brain system...")
        
        provider = config.LLM_PROVIDER.lower()
        api_key = config.API_KEY
        model = config.MODEL_NAME
        
        # Skip if no provider configured
        if not provider or provider == "none":
            print("ℹ️ No legacy LLM configured. Setting Rules Brain as fallback.")
            self.manager.set_fallback_brain("rules")
            return
        
        # Create Brain config based on legacy provider
        if provider == "ollama":
            brain_config = BrainConfig(
                id="ollama_default",
                name="Ollama (Migrated)",
                provider="ollama",
                config_data={
                    "host": config.OLLAMA_HOST,
                    "model": model,
                    "temperature": 0.2,
                    "max_tokens": 256
                },
                is_active=True,
                is_fallback=False
            )
            brain = OllamaBrain(brain_config)
            
        elif provider == "google":
            brain_config = BrainConfig(
                id="google_default",
                name="Google Gemini (Migrated)",
                provider="google",
                config_data={
                    "api_key": api_key,
                    "model": model,
                    "temperature": 0.2
                },
                is_active=True,
                is_fallback=False
            )
            brain = GoogleBrain(brain_config)
            
        elif provider == "openai":
            brain_config = BrainConfig(
                id="openai_default",
                name="OpenAI (Migrated)",
                provider="openai",
                config_data={
                    "api_key": api_key,
                    "model": model,
                    "temperature": 0.2
                },
                is_active=True,
                is_fallback=False
            )
            brain = OpenAIBrain(brain_config)
        else:
            print(f"⚠️ Unknown legacy provider: {provider}")
            self.manager.set_fallback_brain("rules")
            return
        
        # Register and save
        self.manager.register_brain(brain)
        self.manager.set_active_brain(brain.id)
        self.manager.set_fallback_brain("rules")
        
        # Persist to database
        self._save_brain_to_db(brain)
        
        print(f"✅ Migrated legacy '{provider}' configuration to Brain system")
    
    def _save_brain_to_db(self, brain):
        """Save a Brain configuration to database."""
        capabilities = [cap.value for cap in brain.get_capabilities()]
        storage.save_brain_config(
            brain.id,
            brain.name,
            brain.provider,
            brain.get_privacy_level().value,
            brain.config.config_data,
            capabilities
        )
    
    def _load_active_brain(self):
        """Load active Brain from configuration."""
        # Check for rules-only mode
        rules_only = config.defaults.get("RULES_ONLY_MODE", False)
        if rules_only:
            self.manager.set_rules_only_mode(True)
            return
        
        # Active Brain is already set during restore/migration
        active = self.manager.get_active_brain()
        if active:
            print(f"🧠 Active Brain: {active.name}")
        else:
            print("ℹ️ No active Brain configured. Using Rules Brain.")
            self.manager.set_fallback_brain("rules")
    
    def reload_config(self):
        """Reload configuration and re-initialize Brains."""
        print("🧠 Brain: Reloading configuration...")
        # Re-initialize the entire Brain system
        self._initialize_brains()
        self._load_active_brain()
        print("🧠 Brain: Configuration reloaded")
    
    def process(self, command):
        """
        Process a command using the tiered intent pipeline.
        
        Maintains backward compatibility with existing AVA code.
        """
        if not command:
            return None
        
        # Log user query
        storage.log_interaction("user", command)
        
        # Get response
        response = self._get_response(command)
        
        # Log assistant response
        if response:
            res_text = response.get("text") if isinstance(response, dict) else str(response)
            tool_call = response.get("exec_str") if isinstance(response, dict) else None
            storage.log_interaction("avva", res_text, tool_call)
        
        return response
    
    def _get_response(self, command):
        """Internal helper to get response from tiers."""
        # --- TIER 1/2: Local Intent Matching (Static + Parametric) ---
        exec_str = skill_manager.get_intent_match(command)
        if exec_str:
            print(f"System: Intent Match found for '{exec_str}'")
            return skill_manager.execute(exec_str)
        
        # --- TIER 3: LLM Brain Reasoning ---
        # Check for AI permission
        allowed = storage.get_allowed_permissions()
        if "ai.generate" not in allowed:
            print("🔒 LLM skipped: 'ai.generate' permission not granted.")
            return "I can't process that because AI access is currently disabled in Security Settings."
        
        # Select appropriate Brain
        context = self._build_context(command)
        brain = self.manager.select_brain(context)
        
        if not brain:
            return "I heard you, but I couldn't find a direct skill match and no Brain is available."
        
        print(f"DEBUG: Active Brain Selected: {brain.name} ({brain.provider})")
        
        # Filter context based on Brain's privacy level
        filtered_context = ContextFilter.filter_for_privacy_level(
            context,
            brain.get_privacy_level(),
            brain.config.context_filter_level
        )
        
        # Execute with Brain
        print(f"DEBUG: Executing with {brain.name}...")
        brain_response = brain.execute(command, filtered_context, {})
        print(f"DEBUG: Brain Response Success: {brain_response.success}")
        
        # Log usage if applicable
        if brain_response.tokens_used and brain_response.cost_usd:
            storage.log_brain_usage(brain.id, brain_response.tokens_used, brain_response.cost_usd)
        
        # Handle response
        if not brain_response.success:
            print(f"DEBUG: Brain Execution Failed: {brain_response.error}")
            return brain_response.error or "Brain execution failed"
        
        # If Brain extracted an intent, execute it
        if brain_response.intent and brain_response.confidence > 0.7:
            # Construct execution string
            if brain_response.arguments:
                arg_vals = [f'"{v}"' if isinstance(v, str) else str(v) for v in brain_response.arguments.values()]
                exec_str = f"{brain_response.intent}({', '.join(arg_vals)})"
            else:
                exec_str = f"{brain_response.intent}()"
            
            print(f"System: Brain Intent Match ({brain_response.intent}) with {int(brain_response.confidence*100)}% confidence.")
            return skill_manager.execute(exec_str)
        
        # Return natural response
        return brain_response.natural_response or brain_response.content
    
    def _build_context(self, command):
        """Build context dictionary for Brain execution."""
        return {
            "query": command,
            "user": config.NAME,
            "sensitive": False,  # Could be enhanced with sensitivity detection
            "requires_privacy": False
        }


# Global instance
brain = Brain()
