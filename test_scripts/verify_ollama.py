from core.brain import Brain
import json
from unittest.mock import patch, MagicMock

print("--- AVVA Ollama Integration Verification ---")

# Mocking Config for Ollama
with patch('core.config.config.LLM_PROVIDER', 'ollama'), \
     patch('core.config.config.MODEL_NAME', 'llama3'):
    
    test_brain = Brain()
    print(f"Brain LLM Provider: {test_brain.llm_provider}")
    print(f"LLM Ready: {test_brain.llm_ready}")

    # Mock Ollama response
    mock_response = {
        'message': {
            'content': json.dumps({
                "intent": "get_time",
                "arguments": {},
                "confidence": 0.98,
                "natural_response": "Checking the clock for you."
            })
        }
    }

    with patch('ollama.chat', return_value=mock_response):
        print("\n[Test 1] Testing Intent Extraction (get_time) via Complex Phrase")
        # Use a phrase that fails Tier 1/2 regex but Ollama can handle
        result = test_brain.process("Please inform me about the current temporal status of our solar cycle.")
        print(f"Result: {result}")
        assert "current time is" in result.lower()

    # Mock ambiguous/conversational response
    mock_chat_response = {
        'message': {
            'content': json.dumps({
                "intent": None,
                "arguments": {},
                "confidence": 0.0,
                "natural_response": "Hello! I am your assistant. How can I help you today?"
            })
        }
    }

    with patch('ollama.chat', return_value=mock_chat_response):
        print("\n[Test 2] Testing Conversational Response (No Intent)")
        result = test_brain.process("Hey there, how's it going?")
        print(f"Result: {result}")
        assert "Hello" in result

    print("\n✅ Verification Successful: Brain correctly handles Ollama's structured JSON output.")
