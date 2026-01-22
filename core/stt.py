import sounddevice as sd
import numpy as np
import speech_recognition as sr
import io
import scipy.io.wavfile as wav
from core.config import config

def listen():
    """Listens for microphone input using sounddevice and returns recognized text."""
    fs = 44100  # Sample rate
    duration = 5  # Recording duration in seconds
    
    try:
        print(f"Listening for {duration} seconds...")
        # Record audio using InputStream for better stability
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            recording, overflowed = stream.read(int(duration * fs))
        
        print("Processing...")

        # Convert the NumPy array to a WAV file in memory
        byte_io = io.BytesIO()
        wav.write(byte_io, fs, recording)
        byte_io.seek(0)

        # Use SpeechRecognition to process the audio from the memory buffer
        r = sr.Recognizer()
        with sr.AudioFile(byte_io) as source:
            audio = r.record(source)

        query = r.recognize_google(audio, language=config.LANGUAGE)
        print(f"User: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""
    except Exception as e:
        print(f"Audio Error: {e}")
        return ""
