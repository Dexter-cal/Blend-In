from mathutils import Euler

# In a real implementation, this would be the output of a text-to-pose AI model.
# For now, it's a hard-coded dictionary of poses.
# The rotations are in Euler angles (XYZ) for easier authoring.
DREAM_POSES = {
    "sad": {
        "head": (25, 0, 0),   # Head tilted down
        "spine": (15, 0, 0),    # Slumped forward
    },
    "happy": {
        "head": (-10, 0, 0),  # Head tilted slightly up
        "left_shoulder": (0, -15, 0), # Arms back
        "right_shoulder": (0, 15, 0),
    },
    "surprised": {
        "head": (-20, 0, 0),
        "left_shoulder": (0, -45, 0),
        "right_shoulder": (0, 45, 0),
    }
}

class DreamCapture:
    def get_pose_for_prompt(self, prompt):
        """
        Returns the pose data for a given text prompt.
        In the future, this will query an AI model.
        """
        # Simple keyword matching for the prototype
        for keyword, pose_data in DREAM_POSES.items():
            if keyword in prompt.lower():
                return pose_data
        return None

    def apply_pose_to_armature(self, armature, pose_data):
        """
        Applies a pose to the given armature.
        """
        if not armature or not pose_data or armature.mode != 'POSE':
            return

        for bone_name, rotation_euler in pose_data.items():
            pose_bone = armature.pose.bones.get(bone_name)
            if pose_bone:
                # Convert degrees to radians for Blender
                rot_rad = [r * (3.14159 / 180.0) for r in rotation_euler]

                if pose_bone.rotation_mode != 'XYZ':
                    pose_bone.rotation_mode = 'XYZ' # Use Euler for simplicity

                # We can choose to layer this on top or set it directly.
                # For a static pose, setting it directly is fine.
                pose_bone.rotation_euler = Euler(rot_rad, 'XYZ')
