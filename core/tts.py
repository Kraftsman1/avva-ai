from gtts import gTTS
from pygame import mixer
import os
from core.config import config

def speak(text):
    """Converts text to speech and plays it."""
    print(f"{config.NAME}: {text}")
    try:
        # Create audio file
        tts = gTTS(text=text, lang=config.LANGUAGE)
        filename = 'response.mp3'
        tts.save(filename)
        
        # Play audio
        mixer.init()
        mixer.music.load(filename)
        mixer.music.play()
        
        # Wait for audio to finish (simple way)
        while mixer.music.get_busy():
            continue
            
        mixer.quit()
        # Optional: clean up file
        # os.remove(filename)
    except Exception as e:
        print(f"Error in TTS: {e}")
