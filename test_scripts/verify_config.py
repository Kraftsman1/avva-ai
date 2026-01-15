import os
import shutil
from pathlib import Path
from core.config import config
from core.brain import brain

def verify_persistence():
    print("🧪 Testing Config Persistence...")
    
    # 1. Clean previous run
    if config.config_file.exists():
        os.remove(config.config_file)
        
    # 2. Save a new value
    print("   - Saving LLM_PROVIDER = 'openai'...")
    config.save_config("LLM_PROVIDER", "openai")
    
    # 3. Verify File
    if config.config_file.exists():
        print("     ✅ JSON file created.")
        with open(config.config_file, 'r') as f:
            content = f.read()
            if '"LLM_PROVIDER": "openai"' in content:
                print("     ✅ JSON content matches.")
            else:
                print(f"     ❌ JSON content mismatch: {content}")
    else:
        print("     ❌ JSON file NOT created.")
        return

    # 4. Verify In-Memory Update
    if config.LLM_PROVIDER == "openai":
        print("     ✅ In-memory config updated.")
    else:
        print(f"     ❌ In-memory config mismatch: {config.LLM_PROVIDER}")

    # 5. Test Brain Reload
    print("\n🧠 Testing Brain Reload...")
    # Mocking init to avoid actual API calls
    original_init = brain._init_llm
    brain._init_llm = lambda: print("     ✅ Mock LLM Init called.")
    
    brain.reload_config()
    
    # Cleanup
    brain._init_llm = original_init
    os.remove(config.config_file)
    print("\n✅ Config Persistence Verified.")

if __name__ == "__main__":
    verify_persistence()
