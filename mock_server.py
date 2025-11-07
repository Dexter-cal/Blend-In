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
    """Sends a comprehensive mock data packet to the client."""
    while True:
        t = time.time()

        # --- Skeletal Data ---
        head_rot = axis_angle_to_quaternion([1, 0, 0], math.sin(t) * 0.5)
        shoulder_rot = axis_angle_to_quaternion([0, 1, 0], math.sin(t * 1.5) * 0.4)
        skeletal_data = [
            {"name": "head", "rotation": head_rot},
            {"name": "neck", "rotation": [1, 0, 0, 0]},
            {"name": "hip", "rotation": [1, 0, 0, 0]},
            {"name": "left_shoulder", "rotation": shoulder_rot},
            {"name": "right_shoulder", "rotation": shoulder_rot},
            {"name": "spine", "rotation": [1, 0, 0, 0]}
        ]

        # --- Facial Landmark Data ---
        # Simulate mouth opening and closing
        mouth_open_factor = (math.sin(t * 3) + 1) / 40 # small vertical movement
        # Simulate eyebrow raising
        eyebrow_raise_factor = (math.cos(t * 2) + 1) / 30

        facial_landmarks = {
            "lip_upper": [0, 0.05 + mouth_open_factor, 0],
            "lip_lower": [0, 0.03 - mouth_open_factor, 0],
            "eyebrow_left": [-0.03, 0.1 + eyebrow_raise_factor, 0],
            "eyebrow_right": [0.03, 0.1 + eyebrow_raise_factor, 0]
        }

        # --- Vocal Data ---
        vocal_energy = (math.sin(t * 2.5) + 1) / 2 # Fluctuates between 0 and 1

        # --- Eye Gaze Data ---
        eye_gaze_x = math.sin(t * 0.8) * 0.8 # Horizontal gaze
        eye_gaze_y = math.cos(t * 0.6) * 0.6 # Vertical gaze
        eye_gaze_data = [eye_gaze_x, eye_gaze_y]

        # --- Combined Packet ---
        mock_data = {
            "joints": skeletal_data,
            "facial_landmarks": facial_landmarks,
            "vocal_energy": vocal_energy,
            "eye_gaze": eye_gaze_data
        }

        await websocket.send(json.dumps(mock_data))
        await asyncio.sleep(1/60) # 60fps

start_server = websockets.serve(send_mock_data, "localhost", 8765)

print("Mock server started on ws://localhost:8765, sending comprehensive data packets.")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
