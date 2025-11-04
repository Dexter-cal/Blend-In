import asyncio
import websockets
import json
import time
import math

async def send_mock_data(websocket, path):
    """Sends mock skeleton data to the client."""
    while True:
        t = time.time()
        mock_data = {
            "joints": [
                {"name": "head", "position": [math.sin(t), 0, math.cos(t)]},
                {"name": "neck", "position": [math.sin(t) * 0.8, -0.2, math.cos(t) * 0.8]},
                {"name": "hip", "position": [0, -1, 0]},
                {"name": "left_shoulder", "position": [math.sin(t + math.pi / 2) * 0.5, 0, math.cos(t + math.pi / 2) * 0.5]},
                {"name": "right_shoulder", "position": [math.sin(t - math.pi / 2) * 0.5, 0, math.cos(t - math.pi / 2) * 0.5]},
            ]
        }
        await websocket.send(json.dumps(mock_data))
        await asyncio.sleep(1/60) # 60fps

start_server = websockets.serve(send_mock_data, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
