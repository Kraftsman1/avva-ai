import threading
import time
from core.stt import listen
from core.tts import speak, speak_interrupt
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
        self.state = "idle"
        self._interrupt_event = threading.Event()
        self._current_request_id = None
        self._current_thread = None
        
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
        from core.memory import memory

        print(f"🎯 Processing command: {command[:50]}... (id: {request_id})")

        self._interrupt_event.clear()
        self._current_request_id = request_id

        self._emit("assistant.command", {"command": command, "request_id": request_id})
        memory.add_user_message(command)
        self.update_state("thinking")

        try:
            if stream:
                has_streamed = False
                streaming_complete = False
                full_text = ""

                def on_chunk(chunk):
                    nonlocal has_streamed, streaming_complete, full_text
                    if self._interrupt_event.is_set():
                        streaming_complete = True
                        return
                    full_text += chunk
                    self._emit(
                        "assistant.stream",
                        {"chunk": chunk, "done": False, "request_id": request_id}
                    )
                    if not has_streamed:
                        has_streamed = True
                        self.update_state("speaking")

                text, data = brain.process_stream(command, on_chunk)

                if streaming_complete:
                    print("⏹️ Streaming interrupted")
                    self.update_state("idle")
                    return

                self._emit(
                    "assistant.stream",
                    {"done": True, "request_id": request_id}
                )

                if full_text:
                    print(f"✅ Streaming complete, {len(full_text)} chars")
                    memory.add_assistant_message(full_text)
                    self._emit("assistant.response", {"text": full_text, "data": data or {}, "request_id": request_id})
                    self.update_state("speaking")
                    speak(full_text)
                else:
                    print("⚠️ No text from streaming")
                    self.update_state("idle")
            else:
                response = brain.process(command)

                if response:
                    if isinstance(response, dict):
                        text = response.get("text")
                        data = response
                    else:
                        text = response
                        data = None

                    if text:
                        print(f"✅ Response: {text[:100]}...")
                        memory.add_assistant_message(text)
                    self._emit("assistant.response", {"text": text, "data": data, "request_id": request_id})
                    if not self._interrupt_event.is_set():
                        self.update_state("speaking")
                        speak(text)
        except Exception as e:
            import traceback
            print(f"❌ Error processing command: {e}")
            traceback.print_exc()
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
            self._current_request_id = None
            if self.state != "idle":
                self.update_state("idle")

    def interrupt(self):
        """Interrupt the current command processing."""
        self._interrupt_event.set()
        speak_interrupt()

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
