from gtts import gTTS
from pygame import mixer
import os
from core.config import config

def speak(text):
    """Converts text to speech and plays it."""
    print(f"{config.NAME}: {text}")
    try:
        # Create temp directory if it doesn't exist
        os.makedirs('temp/media', exist_ok=True)
        filename = os.path.join('temp/media', 'response.mp3')
        
        # Create audio file
        tts = gTTS(text=text, lang=config.LANGUAGE)
        tts.save(filename)
        
        # Play audio
        mixer.init()
        mixer.music.load(filename)
        mixer.music.play()
        
        # Wait for audio to finish
        while mixer.music.get_busy():
            continue
            
        mixer.quit()
    except Exception as e:
        print(f"Error in TTS: {e}")
