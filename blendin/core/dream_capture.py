from mathutils import Euler
import bpy
import os
import time

class DreamCapture:

    def get_animation_for_prompt(self, prompt):
        """
        Returns animation data for a given text prompt by calling a generative AI API.
        For now, this is mocked to return a sample BVH file.
        """
        # --- MOCKED API CALL ---
        # This simulates a network delay
        time.sleep(3)

        # In a real implementation, you would make an HTTP request to the DeepMotion API here
        # using the client_id and client_secret from the addon preferences.
        #
        # Example (conceptual):
        # prefs = bpy.context.preferences.addons[__package__].preferences
        # client_id = prefs.client_id
        # client_secret = prefs.client_secret
        #
        # if not client_id or not client_secret:
        #     raise Exception("API credentials not set in addon preferences.")
        #
        # animation_data = self.call_deepmotion_api(prompt, client_id, client_secret)

        # For the mock, we will read the local BVH file if the prompt contains "wave"
        if "wave" in prompt.lower():
            bvh_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_wave.bvh')
            with open(bvh_path, 'r') as f:
                animation_data = f.read()
            return animation_data

        return None

    def apply_animation_to_armature(self, armature, bvh_data):
        """
        Parses BVH data and applies it as a new animation action to the armature.
        """
        if not armature or not bvh_data:
            return

        lines = bvh_data.strip().split('\n')

        # --- Simple Parser Logic ---
        motion_started = False
        frame_count = 0
        frame_time = 0.0
        bone_channels = []

        line_iter = iter(lines)

        for i, line in enumerate(line_iter):
            line = line.strip()
            if "MOTION" in line:
                motion_started = True
                # Next lines are Frames and Frame Time
                frame_count = int(next(line_iter).strip().split(' ')[1])
                frame_time = float(next(line_iter).strip().split(' ')[2])
                motion_data_start = i + 4
                break

            if "CHANNELS" in line:
                parts = line.split(' ')
                num_channels = int(parts[1])
                # Find the bone name from the previous line
                prev_line = lines[i-1].strip()
                bone_name = prev_line.split(' ')[1]

                bone_channels.append({
                    "name": bone_name,
                    "channels": parts[2:2+num_channels]
                })

        # --- Apply Animation ---
        if not motion_started or frame_count == 0:
            print("Could not find motion data in BVH.")
            return

        if not armature.animation_data:
            armature.animation_data_create()
        action = bpy.data.actions.new(name="DreamCaptureBVH")
        armature.animation_data.action = action

        motion_lines = lines[motion_data_start:motion_data_start + frame_count]

        channel_index = 0
        for bone_info in bone_channels:
            bone_name = bone_info["name"]
            pose_bone = armature.pose.bones.get(bone_name)

            if not pose_bone:
                channel_index += len(bone_info["channels"])
                continue

            for channel_type in bone_info["channels"]:
                fcurve = None
                if "position" in channel_type.lower():
                    axis_char = channel_type[0].lower()
                    axis_idx = 'xyz'.find(axis_char)
                    if fcurve is None:
                         fcurve = action.fcurves.new(data_path=f'pose.bones["{bone_name}"].location', index=axis_idx)

                elif "rotation" in channel_type.lower():
                    axis_char = channel_type[0].lower()
                    axis_idx = 'xyz'.find(axis_char)
                    pose_bone.rotation_mode = 'XYZ' # Ensure correct rotation mode
                    if fcurve is None:
                        fcurve = action.fcurves.new(data_path=f'pose.bones["{bone_name}"].rotation_euler', index=axis_idx)

                if fcurve:
                    for frame_idx, line in enumerate(motion_lines):
                        value = float(line.strip().split(' ')[channel_index])
                        if "rotation" in channel_type.lower():
                             value *= (3.14159 / 180.0) # Convert to radians
                        fcurve.keyframe_points.insert(frame_idx, value)

                channel_index += 1
