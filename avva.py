from core.stt import listen
from core.tts import speak
from core.brain import brain
from core.config import config

def main():
    speak(f"Hello. I am {config.NAME}. How may I help you today?")
    
    while True:
        # 1. Listen for input
        command = listen()
        
        if not command:
            continue
            
        print(f"\nUser: {command}")
            
        # 2. Process command (Brain)
        response = brain.process(command)
        
        # 3. Speak response
        if response:
            text = response["text"] if isinstance(response, dict) else response
            print(f"AVVA: {text}")
            speak(text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down AVVA. Goodbye!")
