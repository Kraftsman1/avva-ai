# Brain Providers

This directory contains all Brain provider implementations for AVA's configurable LLM system.

## Available Brains

### Local Brains (Fully Offline)

#### Rules Brain (`rules_brain.py`)
- **Provider**: Built-in
- **Privacy**: Fully local
- **Capabilities**: Offline only
- **Description**: Deterministic fallback Brain using intent matching. Works without any LLM.
- **Use Case**: Ultimate fallback, privacy-first mode

#### Ollama Brain (`ollama_brain.py`)
- **Provider**: Ollama
- **Privacy**: Fully local
- **Capabilities**: Chat, JSON mode, Offline, (Vision for llava models)
- **Description**: Local LLM provider using Ollama backend
- **Setup**: Install Ollama and pull models (e.g., `ollama pull llama3`)

#### LM Studio Brain (`lmstudio_brain.py`)
- **Provider**: LM Studio
- **Privacy**: Fully local
- **Capabilities**: Chat, JSON mode, Offline, Streaming
- **Description**: Local LLM using LM Studio's OpenAI-compatible API
- **Setup**: Install LM Studio and load a model

### Cloud Brains

#### Google Gemini Brain (`google_brain.py`)
- **Provider**: Google
- **Privacy**: Trusted Cloud (First-party)
- **Capabilities**: Chat, Tool Calling, JSON mode, Vision (1.5+ models)
- **Description**: Google's Gemini API
- **Setup**: Requires Google API key
- **Cost**: ~$0.075-0.30 per 1M tokens (varies by model)

#### OpenAI Brain (`openai_brain.py`)
- **Provider**: OpenAI
- **Privacy**: External Cloud
- **Capabilities**: Chat, Tool Calling, JSON mode, Streaming, Vision (GPT-4o)
- **Description**: OpenAI's GPT models
- **Setup**: Requires OpenAI API key
- **Cost**: ~$0.15-10.00 per 1M tokens (varies by model)

#### Claude Brain (`claude_brain.py`)
- **Provider**: Anthropic
- **Privacy**: External Cloud
- **Capabilities**: Chat, Tool Calling, Streaming, Vision (Claude 3+)
- **Description**: Anthropic's Claude models
- **Setup**: Requires Anthropic API key
- **Cost**: ~$0.25-15.00 per 1M tokens (varies by model)

## Creating a New Brain Provider

To add a new Brain provider:

1. **Create a new file** in this directory (e.g., `my_brain.py`)

2. **Inherit from `BaseBrain`**:
```python
from core.brains.base import BaseBrain
from core.brain_interface import (
    BrainCapability,
    BrainConfig,
    BrainHealth,
    BrainResponse,
    BrainStatus,
    PrivacyLevel
)

class MyBrain(BaseBrain):
    def __init__(self, config: BrainConfig):
        super().__init__(config)
        # Initialize your provider
    
    def get_capabilities(self) -> List[BrainCapability]:
        return [BrainCapability.CHAT, BrainCapability.OFFLINE]
    
    def get_privacy_level(self) -> PrivacyLevel:
        return PrivacyLevel.LOCAL
    
    def health_check(self) -> BrainHealth:
        # Check if your provider is available
        return BrainHealth(
            status=BrainStatus.AVAILABLE,
            message="Ready"
        )
    
    def execute(self, prompt, context, constraints) -> BrainResponse:
        # Execute reasoning with your provider
        return self._build_success_response(
            content="response",
            confidence=0.9
        )
```

3. **Register your Brain** in `brain.py`:
```python
from core.brains.my_brain import MyBrain

# In _restore_brain method:
elif brain_data['provider'] == 'my_provider':
    brain = MyBrain(brain_config)
```

## Brain Interface Contract

All Brains must implement:

- `get_capabilities()` - Return list of supported capabilities
- `get_privacy_level()` - Return privacy classification
- `health_check()` - Verify provider availability
- `execute(prompt, context, constraints)` - Perform reasoning

Optional methods:
- `estimate_cost(prompt)` - Estimate cost for cloud providers

## Privacy Levels

- **LOCAL**: Fully offline, no network required
- **TRUSTED_CLOUD**: First-party cloud (Google, OpenAI official)
- **EXTERNAL_CLOUD**: Third-party services

## Capabilities

- **CHAT**: Free-form conversational reasoning
- **TOOL_CALLING**: Structured function calling
- **JSON_MODE**: Guaranteed JSON output
- **STREAMING**: Token-by-token streaming
- **VISION**: Image input processing
- **OFFLINE**: No network required
