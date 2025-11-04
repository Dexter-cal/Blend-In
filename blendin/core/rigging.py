import bpy
from mathutils import Vector

class AutoRigOperator(bpy.types.Operator):
    """Operator to create a humanoid armature based on the selected mesh."""
    bl_idname = "blendin.auto_rig"
    bl_label = "Auto-Rig Humanoid"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        mesh_obj = context.active_object

        # Create a new armature
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=mesh_obj.location)
        armature_obj = context.view_layer.objects.active
        armature_obj.name = f"{mesh_obj.name}_Rig"

        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = armature_obj.data.edit_bones

        # Get mesh dimensions
        dims = mesh_obj.dimensions
        min_z = mesh_obj.bound_box[0][2] * mesh_obj.scale.z + mesh_obj.location.z

        # Define bone positions based on bounding box
        # This is a very rough approximation
        z_hip = min_z + dims.z * 0.45
        z_neck = min_z + dims.z * 0.75
        z_head = min_z + dims.z * 0.9
        z_top = min_z + dims.z

        x_shoulder = dims.x * 0.2

        # Create bones
        hip = edit_bones.new('hip')
        hip.head = (0, 0, z_hip)
        hip.tail = (0, 0, z_hip + 0.1) # small bone

        spine = edit_bones.new('spine')
        spine.head = (0, 0, z_hip)
        spine.tail = (0, 0, z_neck)
        spine.parent = hip

        neck = edit_bones.new('neck')
        neck.head = (0, 0, z_neck)
        neck.tail = (0, 0, z_head)
        neck.parent = spine

        head = edit_bones.new('head')
        head.head = (0, 0, z_head)
        head.tail = (0, 0, z_top)
        head.parent = neck

        shoulder_l = edit_bones.new('left_shoulder')
        shoulder_l.head = (x_shoulder, 0, z_neck)
        shoulder_l.tail = (x_shoulder + 0.1, 0, z_neck)
        shoulder_l.parent = spine

        shoulder_r = edit_bones.new('right_shoulder')
        shoulder_r.head = (-x_shoulder, 0, z_neck)
        shoulder_r.tail = (-x_shoulder - 0.1, 0, z_neck)
        shoulder_r.parent = spine

        bpy.ops.object.mode_set(mode='OBJECT')

        # Parent mesh to armature
        mesh_obj.parent = armature_obj
        modifier = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
        modifier.object = armature_obj

        self.report({'INFO'}, f"Created and parented {armature_obj.name}")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(AutoRigOperator)

def unregister():
    bpy.utils.unregister_class(AutoRigOperator)
