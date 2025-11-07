import bpy

class BoneMapping(bpy.types.PropertyGroup):
    source_bone: bpy.props.StringProperty()
    target_bone: bpy.props.StringProperty()

def apply_retargeting(armature, source_rotations, bone_mappings):
    """
    Applies rotations to a target armature based on a bone mapping.
    """
    if not armature or not source_rotations or not bone_mappings or armature.mode != 'POSE':
        return

    mapping_dict = {mapping.source_bone: mapping.target_bone for mapping in bone_mappings}

    for source_bone_name, rotation in source_rotations.items():
        if source_bone_name in mapping_dict:
            target_bone_name = mapping_dict[source_bone_name]
            pose_bone = armature.pose.bones.get(target_bone_name)
            if pose_bone:
                if pose_bone.rotation_mode != 'QUATERNION':
                    pose_bone.rotation_mode = 'QUATERNION'

                # Get the bone's rest pose rotation
                rest_pose_rot = pose_bone.bone.matrix_local.to_quaternion()
                rest_pose_rot.invert()

                # Apply the rotation relative to the rest pose
                pose_bone.rotation_quaternion = rest_pose_rot @ rotation
