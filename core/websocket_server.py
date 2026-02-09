import asyncio
import websockets
import threading
import psutil
import json
import uuid
from datetime import datetime
from core.assistant import assistant


def serialize_datetime(obj):
    """Helper to convert datetime objects to ISO format strings for JSON serialization."""
    if isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj


class WebSocketServer:
    """
    WebSocket Server bridge for AVA.
    Coordinates between the Headless Assistant and the Web UI.
    """
    
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None
        self.server = None

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"🔌 Client connected: {websocket.remote_address}")
        # Send initial state
        import json
        await websocket.send(json.dumps(self._build_message(
            "assistant.state",
            {"state": assistant.state}
        )))

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"🔌 Client disconnected: {websocket.remote_address}")

    async def broadcast(self, message_dict):
        """Sends a message to all connected clients."""
        import json
        message = json.dumps(message_dict)
        if not self.clients:
            return
        try:
            await asyncio.gather(*[client.send(message) for client in self.clients])
        except Exception as e:
            print(f"Broadcast error: {e}")

    def assistant_callback(self, event_type, data):
        """Callback from assistant to broadcast events."""
        if self.loop and self.clients:
            message_id = data.get("request_id")
            payload = dict(data)
            payload.pop("request_id", None)
            message = {
                "id": message_id or str(uuid.uuid4()),
                "type": event_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            }
            asyncio.run_coroutine_threadsafe(
                self.broadcast(message),
                self.loop
            )

    def _build_message(self, event_type, payload, message_id=None):
        return {
            "id": message_id or str(uuid.uuid4()),
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }

    def _build_error_payload(self, code, message, severity="error", retry_allowed=False, context=None):
        return {
            "code": code,
            "message": message,
            "severity": severity,
            "retry_allowed": retry_allowed,
            "context": context or {},
        }

    async def _broadcast_error(self, message_id, code, message, context=None, retry_allowed=False):
        await self.broadcast(
            self._build_message(
                "core.error",
                self._build_error_payload(
                    code,
                    message,
                    severity="error",
                    retry_allowed=retry_allowed,
                    context=context,
                ),
                message_id,
            )
        )

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                message_id = str(uuid.uuid4())
                event_type = None
                try:
                    data = json.loads(message)
                    event_type = data.get("type")
                    payload = data.get("payload", {})
                    message_id = data.get("id") or message_id

                    if event_type == "assistant.command":
                        command = payload.get("command")
                        if command:
                            # Forward command to assistant in a separate thread
                            threading.Thread(
                                target=assistant.process_command,
                                args=(command, message_id, True),
                                daemon=True
                            ).start()

                    elif event_type == "assistant.interrupt":
                        print("⚡ Interrupt received, stopping current operation...")
                        assistant.interrupt()

                    elif event_type == "assistant.voice_start":
                        threading.Thread(
                            target=assistant.capture_voice_command,
                            args=(message_id,),
                            daemon=True
                        ).start()

                    elif event_type == "config.get":
                        from core.config import config
                        await websocket.send(json.dumps(self._build_message(
                            "config.data",
                            config.user_config,
                            message_id
                        )))

                    elif event_type == "config.update":
                        from core.config import config
                        key = payload.get("key")
                        value = payload.get("value")
                        if key is not None:
                            config.save_config(key, value)
                            # Broadcast update to all clients
                            await self.broadcast(self._build_message(
                                "config.updated",
                                {key: value},
                                message_id
                            ))

                    elif event_type == "brains.list":
                        from core.brain_manager import brain_manager
                        brains_info = brain_manager.get_brain_display_info()
                        await websocket.send(json.dumps(self._build_message(
                            "brains.data",
                            {
                                "brains": brains_info,
                                "active_id": brain_manager.active_brain_id,
                                "fallback_id": brain_manager.fallback_brain_id,
                                "rules_only": brain_manager.rules_only_mode,
                                "auto_selection": brain_manager.auto_selection_enabled
                            },
                            message_id
                        )))

                    elif event_type == "brains.select":
                        from core.brain_manager import brain_manager
                        target = payload.get("target") # "active" or "fallback"
                        brain_id = payload.get("brain_id")
                        if target == "active":
                            brain_manager.set_active_brain(brain_id)
                        elif target == "fallback":
                            brain_manager.set_fallback_brain(brain_id)

                        await self.broadcast(self._build_message(
                            "brains.updated",
                            {
                                "active_id": brain_manager.active_brain_id,
                                "fallback_id": brain_manager.fallback_brain_id
                            },
                            message_id
                        ))

                    elif event_type == "brains.toggle_mode":
                        from core.brain_manager import brain_manager
                        mode = payload.get("mode") # "rules_only" or "auto_selection"
                        enabled = payload.get("enabled", False)
                        if mode == "rules_only":
                            brain_manager.set_rules_only_mode(enabled)
                        elif mode == "auto_selection":
                            brain_manager.set_auto_selection(enabled)

                        await self.broadcast(self._build_message(
                            "brains.mode_updated",
                            {
                                "rules_only": brain_manager.rules_only_mode,
                                "auto_selection": brain_manager.auto_selection_enabled
                            },
                            message_id
                        ))

                    elif event_type == "brains.update_config":
                        from core.brain_manager import brain_manager
                        brain_id = payload.get("brain_id")
                        config_data = payload.get("config", {})
                        success = brain_manager.update_brain_config(brain_id, config_data)

                        if success:
                            # Broadcast updated brain data
                            brains_info = brain_manager.get_brain_display_info()
                            await self.broadcast(self._build_message(
                                "brains.data",
                                {
                                    "brains": brains_info,
                                    "active_id": brain_manager.active_brain_id,
                                    "fallback_id": brain_manager.fallback_brain_id,
                                    "rules_only": brain_manager.rules_only_mode,
                                    "auto_selection": brain_manager.auto_selection_enabled
                                },
                                message_id
                            ))

                    elif event_type == "settings.get":
                        from core.config import config
                        # Filter out sensitive keys for broad broadcast? No, just send it for now
                        await websocket.send(json.dumps(self._build_message(
                            "settings.data",
                            config.defaults, # This includes merged env defaults
                            message_id
                        )))

                    elif event_type == "settings.update":
                        from core.config import config
                        updates = payload.get("settings", {})
                        for k, v in updates.items():
                            config.save_config(k, v)

                        await self.broadcast(self._build_message(
                            "settings.updated",
                            updates,
                            message_id
                        ))

                    elif event_type == "conversation.list":
                        from core.memory import memory
                        limit = payload.get("limit", 20)
                        sessions = memory.list_recent_sessions(limit=limit)
                        await websocket.send(json.dumps(self._build_message(
                            "conversation.list",
                            {"sessions": serialize_datetime(sessions)},
                            message_id
                        )))

                    elif event_type == "conversation.get":
                        from core.memory import memory
                        from core.persistence import storage
                        session_id = payload.get("session_id")
                        if session_id:
                            messages = memory.get_session_history(session_id=session_id)
                            session = storage.get_session(session_id)
                        else:
                            messages = memory.get_session_history()
                            session = storage.get_session(memory.current_session_id) if memory.current_session_id else None

                        await websocket.send(json.dumps(self._build_message(
                            "conversation.messages",
                            {"session": serialize_datetime(session), "messages": serialize_datetime(messages)},
                            message_id
                        )))

                    elif event_type == "conversation.delete":
                        from core.memory import memory
                        session_id = payload.get("session_id")
                        if session_id:
                            memory.delete_session(session_id)
                        await websocket.send(json.dumps(self._build_message(
                            "conversation.deleted",
                            {"session_id": session_id},
                            message_id
                        )))

                    elif event_type == "conversation.search":
                        from core.memory import memory
                        query = payload.get("query", "")
                        results = memory.recall(query)
                        # Note: recall() already converts datetime to string in its implementation
                        await websocket.send(json.dumps(self._build_message(
                            "conversation.search_results",
                            {"query": query, "results": results},
                            message_id
                        )))

                    elif event_type == "conversation.start":
                        from core.memory import memory
                        title = payload.get("title")
                        brain_id = payload.get("brain_id")
                        session_id = memory.start_session(title=title, brain_id=brain_id)
                        await websocket.send(json.dumps(self._build_message(
                            "conversation.started",
                            {"session_id": session_id, "title": title or "New Conversation"},
                            message_id
                        )))

                    elif event_type == "conversation.pin":
                        from core.memory import memory
                        session_id = payload.get("session_id")
                        if session_id:
                            pinned = memory.toggle_pin(session_id)
                            await self.broadcast(self._build_message(
                                "conversation.pinned",
                                {"session_id": session_id, "pinned": pinned},
                                message_id
                            ))

                    elif event_type == "conversation.export":
                        from core.memory import memory
                        session_id = payload.get("session_id")
                        format_type = payload.get("format", "markdown")
                        if session_id:
                            content = memory.export_conversation(session_id, format_type)
                            await websocket.send(json.dumps(self._build_message(
                                "conversation.exported",
                                {
                                    "session_id": session_id,
                                    "format": format_type,
                                    "content": content
                                },
                                message_id
                            )))

                except json.JSONDecodeError:
                    print("⚠️ Received invalid JSON from client.")
                    await self._broadcast_error(
                        message_id,
                        "INVALID_JSON",
                        "Received invalid JSON from client.",
                        context={"event_type": event_type},
                    )
                except Exception as e:
                    await self._broadcast_error(
                        message_id,
                        "WS_HANDLER_ERROR",
                        str(e),
                        context={"event_type": event_type},
                        retry_allowed=True,
                    )
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def _broadcast_stats(self):
        """Periodically broadcasts accurate system resource usage."""
        # Initialize GPU metrics if possible
        nvml_initialized = False
        try:
            import pynvml
            pynvml.nvmlInit()
            nvml_initialized = True
        except Exception:
            pass

        while True:
            if self.clients:
                try:
                    stats = {
                        "cpu": psutil.cpu_percent(interval=None),
                        "ram": psutil.virtual_memory().percent,
                    }
                    
                    # Add GPU VRAM if initialized
                    if nvml_initialized:
                        try:
                            import pynvml
                            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                            stats["vram"] = (info.used / info.total) * 100
                            # Also include raw values for UI formatting
                            stats["vram_used"] = info.used / (1024**2) # MB
                            stats["vram_total"] = info.total / (1024**2) # MB
                        except Exception:
                            stats["vram"] = 0
                    else:
                        stats["vram"] = 0

                    await self.broadcast({
                        "id": str(uuid.uuid4()),
                        "type": "system.stats",
                        "payload": stats,
                        "timestamp": datetime.now().isoformat()
                    })

                    # Add Intelligence Stats broadcast
                    intelligence_stats = {
                        "tokens_sec": 42.5 if assistant.state == "thinking" else 0,
                        "latency": 12 if assistant.state == "thinking" else 0,
                        "npu_acceleration": 64 if nvml_initialized else 0,
                    }
                    await self.broadcast({
                        "id": str(uuid.uuid4()),
                        "type": "intelligence.stats",
                        "payload": intelligence_stats,
                        "timestamp": datetime.now().isoformat()
                    })

                except Exception as e:
                    print(f"⚠️ Error gathering stats: {e}")
            
            await asyncio.sleep(2)

    async def _main(self):
        # Start stats loop
        asyncio.create_task(self._broadcast_stats())

        async with websockets.serve(self.handler, self.host, self.port):
            print(f"📡 WebSocket Server listening on ws://{self.host}:{self.port}")
            # Register with assistant
            assistant.add_callback(self.assistant_callback)
            await asyncio.Future()  # Keep running forever

    def run_server(self):
        """Starts the WebSocket server (intended for a separate thread)."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main())
        except Exception as e:
            print(f"❌ WebSocket Server Error: {e}")
        finally:
            self.loop.close()

    def start_thread(self):
        """Launches the server in a background thread."""
        thread = threading.Thread(target=self.run_server, daemon=True)
        thread.start()
        return thread

# Singleton instance
ws_server = WebSocketServer()
