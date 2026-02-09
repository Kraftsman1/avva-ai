import threading
import time
from core.stt import listen
from core.tts import speak
from core.brain import brain
from core.config import config
from core.persistence import storage
from core.skill_manager import skill_manager

class Assistant:
    """
    Headless Assistant class that manages the main interaction loop.
    Decoupled from any Gtk dependency.
    """
    
    def __init__(self):
        self.active = True
        self.listening_enabled = True
        self.callbacks = []
        self.state = "idle" # listening, thinking, speaking, idle
        
    def add_callback(self, callback):
        """
        Adds a callback function to be notified of events.
        callback(event_type, data)
        """
        self.callbacks.append(callback)
        
    def _emit(self, event_type, data):
        for cb in self.callbacks:
            try:
                cb(event_type, data)
            except Exception as e:
                print(f"Error in assistant callback: {e}")

    def update_state(self, new_state):
        self.state = new_state
        self._emit("assistant.state", {"state": new_state})

    def process_command(self, command, request_id=None, stream=False):
        """Processes a string command (text or recognized speech)."""
        self._emit("assistant.command", {"command": command, "request_id": request_id})
        self.update_state("thinking")

        try:
            if stream:
                has_streamed = False

                def on_chunk(chunk):
                    nonlocal has_streamed
                    self._emit(
                        "assistant.stream",
                        {"chunk": chunk, "done": False, "request_id": request_id}
                    )
                    if not has_streamed:
                        has_streamed = True
                        self.update_state("speaking")

                text, data = brain.process_stream(command, on_chunk)

                self._emit(
                    "assistant.stream",
                    {"done": True, "request_id": request_id}
                )

                if text:
                    if not has_streamed:
                        self.update_state("speaking")
                    speak(text)
            else:
                response = brain.process(command)

                if response:
                    if isinstance(response, dict):
                        text = response.get("text")
                        data = response
                    else:
                        text = response
                        data = None

                    self._emit("assistant.response", {"text": text, "data": data, "request_id": request_id})
                    self.update_state("speaking")
                    speak(text)
        except Exception as e:
            self._emit(
                "core.error",
                {
                    "code": "BRAIN_PROCESSING_ERROR",
                    "message": str(e),
                    "severity": "error",
                    "retry_allowed": True,
                    "context": {"command": command},
                    "request_id": request_id,
                },
            )
        finally:
            self.update_state("idle")

    def voice_loop(self):
        """Standard background loop for voice interaction."""
        print("🎙️ Starting headless voice loop...")
        while self.active:
            if self.listening_enabled:
                self.update_state("listening")
                command = listen()
                
                if command:
                    self.process_command(command)
                else:
                    # Brief sleep to prevent tight loop if STT returns immediately
                    time.sleep(0.1)
            else:
                time.sleep(0.5)

    def capture_voice_command(self, request_id=None):
        """Capture a single voice command on demand."""
        try:
            self.update_state("listening")
            command = listen()
            if command:
                self.process_command(command, request_id, True)
            else:
                self.update_state("idle")
        except Exception as e:
            self._emit(
                "core.error",
                {
                    "code": "VOICE_CAPTURE_ERROR",
                    "message": str(e),
                    "severity": "error",
                    "retry_allowed": True,
                    "context": {"source": "voice_capture"},
                    "request_id": request_id,
                },
            )
            self.update_state("idle")

    def start_voice_thread(self):
        thread = threading.Thread(target=self.voice_loop, daemon=True)
        thread.start()
        return thread

    def check_startup_permissions(self):
        """Headless version of permission checks."""
        allowed = storage.get_allowed_permissions()
        
        # 1. Microphone Check
        if "audio.record" not in allowed:
            print("🎙️ Requesting Microphone Access...")
            # This will still spawn the Gtk prompt via skill_manager for now
            granted = skill_manager._request_permission("AVVA Core", "audio.record")
            if granted:
                skill_manager.toggle_permission("audio.record", True)
                print("✅ Microphone access granted.")
            else:
                print("❌ Microphone access denied.")
        
        # 2. AI Brain Check (LLM)
        if "ai.generate" not in allowed:
            print("🧠 Requesting AI/LLM Access..." )
            granted = skill_manager._request_permission("AVVA Core", "ai.generate")
            if granted:
                skill_manager.toggle_permission("ai.generate", True)
                print("✅ AI Access granted.")
            else:
                print("❌ AI Access denied. LLM features disabled.")

# Singleton instance
assistant = Assistant()
