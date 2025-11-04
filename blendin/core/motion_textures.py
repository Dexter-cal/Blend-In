import bpy
from mathutils import Quaternion, Euler
from mathutils.noise import noise

class MotionTextureGenerator:
    """
    Generates subtle, procedural idle motions using Perlin noise.
    """
    def __init__(self, speed=0.1, scale=0.5):
        self.speed = speed
        self.scale = scale
        # Use different seeds/offsets for each axis and bone to decorrelate motion
        self.seeds = {
            'spine': {'x': 0, 'y': 10, 'z': 20},
            'head':  {'x': 30, 'y': 40, 'z': 50},
        }

    def get_offsets(self, time):
        """
        Calculates the rotational offsets for various bones at a given time.
        Returns a dictionary of {bone_name: Quaternion_offset}.
        """
        offsets = {}
        t = time * self.speed

        # --- Spine Sway ---
        # Subtle side-to-side and front-to-back sway from the hip
        spine_seed = self.seeds['spine']
        spine_amp = 0.005 # very small amplitude
        spine_rot_x = (noise(t + spine_seed['x']) - 0.5) * spine_amp * 2
        spine_rot_z = (noise(t + spine_seed['z']) - 0.5) * spine_amp * 2

        spine_euler = Euler((spine_rot_x, 0, spine_rot_z), 'XYZ')
        # Apply this to the root bone, e.g., 'hip'
        offsets['hip'] = spine_euler.to_quaternion()

        # --- Head Look ---
        # Subtle "look around" motion for the head
        head_seed = self.seeds['head']
        head_amp = 0.01
        head_rot_y = (noise(t + head_seed['y']) - 0.5) * head_amp * 2 # Yaw
        head_rot_z = (noise(t + head_seed['z']) - 0.5) * head_amp * 1.5 # Roll

        head_euler = Euler((0, head_rot_y, head_rot_z), 'XYZ')
        offsets['head'] = head_euler.to_quaternion()

        return offsets
