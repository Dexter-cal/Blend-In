from mathutils import Euler
import bpy

# This dictionary now stores animation sequences.
# Each key is a prompt keyword, and the value is a list of keyframes.
# Each keyframe has a 'frame' number and a 'pose' dictionary.
DREAM_ANIMATIONS = {
    "sad": [
        {"frame": 1, "pose": {
            "head": (25, 0, 0),   # Head tilted down
            "spine": (15, 0, 0),    # Slumped forward
        }}
    ],
    "happy": [
        {"frame": 1, "pose": {
            "head": (-10, 0, 0),  # Head tilted slightly up
            "left_shoulder": (0, -15, 0), # Arms back
            "right_shoulder": (0, 15, 0),
        }}
    ],
    "wave": [
        {"frame": 1, "pose": {"right_shoulder": (0, 0, 0)}},
        {"frame": 10, "pose": {"right_shoulder": (0, 0, -90)}}, # Arm goes up
        {"frame": 20, "pose": {"right_shoulder": (20, 0, -90)}}, # Wave side 1
        {"frame": 30, "pose": {"right_shoulder": (-20, 0, -90)}}, # Wave side 2
        {"frame": 40, "pose": {"right_shoulder": (0, 0, 0)}}, # Arm goes down
    ]
}

class DreamCapture:
    def get_animation_for_prompt(self, prompt):
        """
        Returns the animation data for a given text prompt.
        In the future, this will query an AI model.
        """
        # Simple keyword matching for the prototype
        for keyword, anim_data in DREAM_ANIMATIONS.items():
            if keyword in prompt.lower():
                return anim_data
        return None

    def apply_animation_to_armature(self, armature, animation_data):
        """
        Applies a sequence of keyframes to the given armature.
        """
        if not armature or not animation_data:
            return

        # Ensure the armature has an action to store the keyframes
        if not armature.animation_data:
            armature.animation_data_create()

        action = bpy.data.actions.new(name="DreamCaptureAnimation")
        armature.animation_data.action = action

        for keyframe in animation_data:
            frame = keyframe['frame']
            pose_data = keyframe['pose']

            for bone_name, rotation_euler in pose_data.items():
                pose_bone = armature.pose.bones.get(bone_name)
                if pose_bone:
                    if pose_bone.rotation_mode != 'XYZ':
                        pose_bone.rotation_mode = 'XYZ'

                    rot_rad = [r * (3.14159 / 180.0) for r in rotation_euler]
                    pose_bone.rotation_euler = Euler(rot_rad, 'XYZ')

                    # Insert keyframes for the rotation
                    pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
