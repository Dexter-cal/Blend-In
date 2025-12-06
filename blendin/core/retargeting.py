import bpy

class BoneMapping(bpy.types.PropertyGroup):
    """Represents a mapping from a source bone to a target bone."""
    source_bone: bpy.props.StringProperty(name="Source Bone")
    target_bone: bpy.props.StringProperty(name="Target Bone")

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
                # This is a simple 1-to-1 rotation copy.
                # A more advanced system would handle axis and rest pose differences.
                if pose_bone.rotation_mode != 'QUATERNION':
                    pose_bone.rotation_mode = 'QUATERNION'
                pose_bone.rotation_quaternion = rotation

def register():
    bpy.utils.register_class(BoneMapping)

def unregister():
    bpy.utils.unregister_class(BoneMapping)
