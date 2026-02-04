from pygame import mixer
import os
import requests
from core.config import config

def speak(text):
    """Orchestrates Text-to-Speech using the configured engine."""
    engine = config.TTS_ENGINE.lower()
    print(f"{config.NAME}: {text}")
    
    # Create temp directory
    os.makedirs('temp/media', exist_ok=True)
    filename = os.path.join('temp/media', 'response.mp3')
    
    try:
        if engine == "gtts":
            _speak_gtts(text, filename)
        elif engine == "openai":
            _speak_openai(text, filename)
        elif engine == "elevenlabs":
            _speak_elevenlabs(text, filename)
        elif engine == "piper":
            # Piper usually outputs WAV
            filename = filename.replace('.mp3', '.wav')
            _speak_piper(text, filename)
        else:
            print(f"Unknown TTS engine: {engine}. Falling back to gTTS.")
            _speak_gtts(text, filename)

        _play_audio(filename)
    except Exception as e:
        print(f"TTS Error ({engine}): {e}")

def _play_audio(filename):
    """Plays the generated audio file."""
    try:
        mixer.init()
        mixer.music.load(filename)
        mixer.music.play()
        while mixer.music.get_busy():
            continue
        mixer.quit()
    except Exception as e:
        print(f"Playback Error: {e}")

def _speak_gtts(text, filename):
    from gtts import gTTS
    tts = gTTS(text=text, lang=config.LANGUAGE)
    tts.save(filename)

def _speak_openai(text, filename):
    from openai import OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(filename)

def _speak_elevenlabs(text, filename):
    from elevenlabs import save
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
    audio = client.generate(
        text=text,
        voice="Rachel",
        model="eleven_multilingual_v2"
    )
    save(audio, filename)

def _speak_piper(text, filename):
    """
    Piper local TTS implementation using standalone binary.
    """
    # 1. Get base directory (where the core script/binary is located)
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 2. Check for binary
    piper_path = os.path.join(base_dir, 'bin', 'piper')
    if not os.path.exists(piper_path):
        # Fallback to current working directory if not found relative to argv[0]
        piper_path = os.path.join(os.getcwd(), 'bin', 'piper')
        
    if not os.path.exists(piper_path):
        print(f"Piper binary not found. Falling back to gTTS.")
        _speak_gtts(text, filename.replace('.wav', '.mp3'))
        return

    # 3. Check for model
    # Prefer temp/models, then models/ in base_dir
    model_path = os.path.join(os.getcwd(), 'temp', 'models', f"{config.PIPER_VOICE}.onnx")
    if not os.path.exists(model_path):
        model_path = os.path.join(base_dir, 'models', f"{config.PIPER_VOICE}.onnx")

    if not os.path.exists(model_path):
        print(f"Piper model not found at {model_path}. Falling back to gTTS.")
        _speak_gtts(text, filename.replace('.wav', '.mp3'))
        return

    # 4. Call piper with LD_LIBRARY_PATH pointed to our bin folder
    bin_dir = os.path.dirname(piper_path)
    command = f'export LD_LIBRARY_PATH="{bin_dir}":$LD_LIBRARY_PATH && echo "{text}" | "{piper_path}" --model "{model_path}" --output_file "{filename}"'
    
    try:
        os.system(command)
    except Exception as e:
        print(f"Error executing Piper: {e}")
        _speak_gtts(text, filename.replace('.wav', '.mp3'))
