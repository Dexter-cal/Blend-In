import asyncio
import websockets
import json
import threading

class WebsocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.thread = None
        self.loop = None
        self.running = False
        self.latest_data = None
        self.lock = threading.Lock()

    def get_latest_data(self):
        with self.lock:
            return self.latest_data

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread:
            self.thread.join()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.listen())
        finally:
            self.loop.close()

    async def listen(self):
        while self.running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    print("Connected to WebSocket server.")
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        with self.lock:
                            self.latest_data = data
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                await asyncio.sleep(5)

client = None

def get_client():
    global client
    return client

def start_client():
    global client
    if client is None:
        client = WebsocketClient("ws://localhost:8765")
        client.start()
    print("WebSocket client started.")

def stop_client():
    global client
    if client:
        client.stop()
        client = None
    print("WebSocket client stopped.")
