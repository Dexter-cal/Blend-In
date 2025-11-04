import asyncio
import websockets
import json
import time
import math

def axis_angle_to_quaternion(axis, angle):
    """Converts an axis-angle rotation to a quaternion."""
    half_angle = angle / 2
    s = math.sin(half_angle)
    w = math.cos(half_angle)
    x = axis[0] * s
    y = axis[1] * s
    z = axis[2] * s
    return [w, x, y, z]

async def send_mock_data(websocket, path):
    """Sends mock skeleton data with quaternion rotations to the client."""
    while True:
        t = time.time()

        # Simple nodding motion for the head (rotation around X-axis)
        head_rot = axis_angle_to_quaternion([1, 0, 0], math.sin(t) * 0.5)

        # Simple twisting motion for the shoulders (rotation around Y-axis)
        shoulder_rot = axis_angle_to_quaternion([0, 1, 0], math.sin(t * 1.5) * 0.4)

        mock_data = {
            "joints": [
                {"name": "head", "rotation": head_rot},
                {"name": "neck", "rotation": [1, 0, 0, 0]}, # Identity quaternion
                {"name": "hip", "rotation": [1, 0, 0, 0]},
                {"name": "left_shoulder", "rotation": shoulder_rot},
                {"name": "right_shoulder", "rotation": shoulder_rot},
                # Add spine to match the auto-rig
                {"name": "spine", "rotation": [1, 0, 0, 0]}
            ]
        }
        await websocket.send(json.dumps(mock_data))
        await asyncio.sleep(1/60) # 60fps

start_server = websockets.serve(send_mock_data, "localhost", 8765)

print("Mock server started on ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
