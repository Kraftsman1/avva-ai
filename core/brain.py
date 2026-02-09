"""
Brain - Facade for the new Brain Manager system.

This module maintains backward compatibility with the existing AVA codebase
while delegating to the new Brain Manager architecture.
"""

from core.brain_manager import brain_manager
from core.brain_interface import BrainConfig, BrainCapability
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
from core.memory import memory


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

    def process_stream(self, command, on_chunk, chunk_size=32):
        """
        Process a command and emit incremental chunks via callback.

        Args:
            command: User input string.
            on_chunk: Callable that receives chunk strings.
            chunk_size: Character size per chunk (fallback for non-streaming brains).

        Returns:
            Tuple of (full_text, data) or (None, None) on failure.
        """
        if not command:
            return None, None

        storage.log_interaction("user", command)

        context = self._build_context(command)
        brain = self.manager.select_brain(context)

        if not brain:
            return None, None

        full_text = ""
        tool_call = None
        used_native_streaming = False

        try:
            if brain.supports_capability(BrainCapability.STREAMING):
                filtered_context = ContextFilter.filter_for_privacy_level(
                    context,
                    brain.get_privacy_level(),
                    brain.config.context_filter_level
                )

                stream_result = brain.execute_stream(command, filtered_context, {})
                if stream_result is not None:
                    for chunk_data in stream_result:
                        if "error" in chunk_data:
                            break
                        if chunk_data.get("done"):
                            full_text = chunk_data.get("full_content", full_text)
                            break
                        chunk = chunk_data.get("chunk", "")
                        if chunk:
                            full_text += chunk
                            on_chunk(chunk)
                            used_native_streaming = True
        except Exception as e:
            print(f"⚠️ Streaming failed for {brain.name}, falling back: {e}")

        if not used_native_streaming:
            response = self._get_response(command)

            if response:
                if isinstance(response, dict):
                    text = response.get("text") or ""
                    data = response
                else:
                    text = str(response)
                    data = None

                for chunk in self._chunk_text(text, chunk_size):
                    on_chunk(chunk)
                full_text = text
                tool_call = data.get("exec_str") if isinstance(data, dict) else None

        storage.log_interaction("avva", full_text, tool_call)
        return full_text, {"exec_str": tool_call} if tool_call else None
    
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
            print("⚠️ No Brain available, cannot process command.")
            return "I heard you, but I couldn't find a direct skill match and no Brain is available."
        
        print(f"DEBUG: Active Brain Selected: {brain.name} ({brain.provider})")
        
        # Try to execute with selected Brain
        brain_response = self._try_brain_execution(brain, command, context)
        
        # If brain execution failed, try fallback chain
        if not brain_response or not brain_response.success:
            print(f"⚠️ Primary Brain failed: {brain_response.error if brain_response else 'No response'}")
            
            # Try fallback brain
            fallback_brain = self.manager._try_fallback(f"Primary Brain '{brain.name}' failed")
            if fallback_brain and fallback_brain.id != brain.id:
                print(f"🔄 Attempting fallback to: {fallback_brain.name}")
                brain_response = self._try_brain_execution(fallback_brain, command, context)
            
            # If still failed, try Rules Brain as last resort
            if not brain_response or not brain_response.success:
                rules_brain = self.manager.get_brain("rules")
                if rules_brain and rules_brain.id != brain.id:
                    print("🔄 Final fallback to Rules Brain")
                    brain_response = self._try_brain_execution(rules_brain, command, context)
        
        # If all brains failed, return error
        if not brain_response or not brain_response.success:
            error_msg = brain_response.error if brain_response else "All brains failed to process command"
            print(f"❌ All brains failed: {error_msg}")
            return f"I'm having trouble processing that command. {error_msg}"
        
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

    @staticmethod
    def _chunk_text(text, chunk_size):
        if not text:
            return
        for start in range(0, len(text), chunk_size):
            yield text[start:start + chunk_size]
    
    def _try_brain_execution(self, brain, command, context):
        """Try to execute command with a specific brain."""
        try:
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
            
            return brain_response
        except Exception as e:
            print(f"❌ Exception during brain execution: {e}")
            from core.brain_interface import BrainResponse
            return BrainResponse(
                success=False,
                content="",
                error=str(e)
            )
    
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
