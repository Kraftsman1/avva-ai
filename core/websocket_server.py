import asyncio
import websockets
import threading
import psutil
import json
from datetime import datetime
from core.assistant import assistant

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
        await websocket.send(json.dumps({
            "type": "assistant.state",
            "payload": {"state": assistant.state},
            "timestamp": datetime.now().isoformat()
        }))

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"🔌 Client disconnected: {websocket.remote_address}")

    async def broadcast(self, message_dict):
        if not self.clients:
            return
            
        import json
        message = json.dumps(message_dict)
        # Create a copy of clients to avoid issues if set changes during iteration
        await asyncio.gather(*[client.send(message) for client in self.clients])

    def assistant_callback(self, event_type, data):
        """Callback from assistant to broadcast events."""
        if self.loop and self.clients:
            asyncio.run_coroutine_threadsafe(
                self.broadcast({
                    "type": event_type,
                    "payload": data,
                    "timestamp": datetime.now().isoformat()
                }),
                self.loop
            )

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get("type")
                    payload = data.get("payload", {})
                    
                    if event_type == "assistant.command":
                        command = payload.get("command")
                        if command:
                            # Forward command to assistant in a separate thread
                            threading.Thread(
                                target=assistant.process_command, 
                                args=(command,), 
                                daemon=True
                            ).start()
                            
                    elif event_type == "assistant.interrupt":
                        # Logic to interrupt assistant
                        assistant.listening_enabled = False
                        assistant.update_state("idle")
                        assistant.listening_enabled = True
                        
                except json.JSONDecodeError:
                    print("⚠️ Received invalid JSON from client.")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def _broadcast_stats(self):
        """Periodically broadcasts system resource usage."""
        while True:
            if self.clients:
                stats = {
                    "cpu": psutil.cpu_percent(),
                    "ram": psutil.virtual_memory().percent,
                    "vram": 0 # Placeholder for GPU stats
                }
                await self.broadcast({
                    "type": "system.stats",
                    "payload": stats,
                    "timestamp": datetime.now().isoformat()
                })
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
