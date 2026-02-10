import threading
import time
from core.stt import listen
from core.tts import speak, speak_interrupt
from core.brain import brain
from core.config import config
from core.persistence import storage
from core.skill_manager import skill_manager
from core.workflow import workflow_manager, Workflow, WorkflowStatus

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
        self._current_workflow_id = None

        # Connect workflow manager callbacks
        workflow_manager.add_callback(self._on_workflow_event)
        
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
                    self.update_state("idle")
                    return

                self._emit(
                    "assistant.stream",
                    {"done": True, "request_id": request_id}
                )

                if full_text:
                    memory.add_assistant_message(full_text)
                    self._emit("assistant.response", {"text": full_text, "data": data or {}, "request_id": request_id})
                    self.update_state("speaking")
                    speak(full_text)
                else:
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
                        memory.add_assistant_message(text)
                    self._emit("assistant.response", {"text": text, "data": data, "request_id": request_id})
                    if not self._interrupt_event.is_set():
                        self.update_state("speaking")
                        speak(text)
        except Exception as e:
            import traceback
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

    def _on_workflow_event(self, event_type: str, data: dict):
        """Forward workflow events to assistant callbacks."""
        self._emit(event_type, data)

    def execute_workflow(self, workflow_id: str, request_id: str = None):
        """
        Execute a workflow step by step.

        Args:
            workflow_id: ID of the workflow to execute
            request_id: Optional request correlation ID
        """
        from core.memory import memory

        self._current_workflow_id = workflow_id
        workflow = workflow_manager.get_workflow(workflow_id)

        if not workflow:
            self._emit("core.error", {
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found",
                "severity": "error",
                "request_id": request_id,
            })
            return

        try:
            self.update_state("thinking")

            while True:
                if self._interrupt_event.is_set():
                    workflow_manager.cancel_workflow(workflow_id)
                    break

                next_step = workflow.get_next_step()
                if not next_step:
                    # No more steps to execute
                    break

                # Start step execution
                workflow_manager.start_step(workflow_id, next_step.id)
                self.update_state("thinking")

                # Execute the step
                try:
                    if next_step.intent:
                        # Execute via skill manager using the intent string
                        exec_str = skill_manager.get_intent_match(next_step.intent)
                        if exec_str:
                            raw = skill_manager.execute(exec_str)
                            result = str(raw) if raw else "Done"
                        else:
                            result = f"No skill matched intent: {next_step.intent}"
                    else:
                        # Execute via brain
                        prompt = f"{next_step.action}\n\nContext: {workflow.global_context}"
                        response = brain.process(prompt)

                        if isinstance(response, dict):
                            result = response.get("text", str(response))
                        else:
                            result = str(response)

                    # Complete step
                    workflow_manager.complete_step(
                        workflow_id,
                        next_step.id,
                        result,
                        {"last_result": result}
                    )

                    # Speak result if not interrupted
                    if not self._interrupt_event.is_set():
                        self.update_state("speaking")
                        speak(f"Step complete: {next_step.description}")

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    workflow_manager.fail_step(
                        workflow_id,
                        next_step.id,
                        str(e)
                    )
                    break

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._emit("core.error", {
                "code": "WORKFLOW_EXECUTION_ERROR",
                "message": str(e),
                "severity": "error",
                "request_id": request_id,
            })

        finally:
            self._current_workflow_id = None
            self.update_state("idle")

    def plan_workflow(self, command: str, request_id: str = None) -> Workflow:
        """
        Plan a multi-step workflow for a complex command.

        Args:
            command: User's complex request
            request_id: Optional request correlation ID

        Returns:
            Created Workflow instance, or None if planning fails
        """
        try:
            # Check if brain supports workflow planning
            active_brain = brain.manager.get_active_brain()
            if not active_brain:
                return None

            from core.brain_interface import BrainCapability
            if not active_brain.supports_capability(BrainCapability.WORKFLOW_PLANNING):
                return None

            # Get available skills for context
            available_skills = dict(skill_manager.static_intents)

            context = {
                "available_skills": available_skills,
                "conversation_history": [],
            }

            # Ask brain to plan workflow
            plan = active_brain.plan_workflow(command, context)

            if not plan:
                return None

            # Create workflow from plan
            workflow = workflow_manager.create_workflow(
                title=plan.get("title", "Multi-step task"),
                description=plan.get("description", command),
                original_request=command,
                steps=plan.get("steps", [])
            )

            return workflow

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._emit("core.error", {
                "code": "WORKFLOW_PLANNING_ERROR",
                "message": str(e),
                "severity": "warning",
                "request_id": request_id,
            })
            return None

# Singleton instance
assistant = Assistant()
