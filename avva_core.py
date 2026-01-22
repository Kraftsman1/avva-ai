#!/usr/bin/env python3
# Headless AVA Core Entry Point
import sys
import os
import time

# Add the current directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.assistant import assistant
from core.websocket_server import ws_server
from core.config import config

def core_callback(event_type, data):
    """Simple callback to log events to the console."""
    if event_type == "assistant.state":
        print(f"🔄 State Change: {data['state'].upper()}")
    elif event_type == "assistant.command":
        print(f"⌨  User Command: {data['command']}")
    elif event_type == "assistant.response":
        print(f"🤖 AVA: {data['text']}")
    elif event_type == "assistant.stream":
        # Handle streaming chunks if implemented later
        pass

def main():
    print(f"🚀 Starting {config.NAME} Headless Core...")
    
    # 1. Setup Callback
    assistant.add_callback(core_callback)
    
    # 2. Check Permissions (Headless mode)
    assistant.check_startup_permissions()
    
    # 3. Start WebSocket Server
    ws_server.start_thread()
    
    # 4. Start Voice Interaction Thread
    assistant.start_voice_thread()
    
    print("✨ Core is active. Press Ctrl+C to shutdown.")
    
    try:
        # Start a simple input thread for text-based debugging
        import threading
        def input_loop():
            while True:
                try:
                    text = input()
                    if text:
                        print(f"⌨  Manual Input: {text}")
                        assistant.process_command(text)
                except EOFError:
                    break
        
        t = threading.Thread(target=input_loop, daemon=True)
        t.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AVA Core. Goodbye!")
        assistant.active = False

if __name__ == "__main__":
    main()
