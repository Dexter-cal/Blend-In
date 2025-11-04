import bpy

class BLENDIN_PT_main_panel(bpy.types.Panel):
    bl_label = "Blend-In"
    bl_idname = "BLENDIN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("blendin.create_sample_armature", text="Create Sample Armature")
        row = layout.row()
        row.operator("wm.live_animation_operator", text="Start Live Animation")


class BLENDIN_OT_create_sample_armature(bpy.types.Operator):
    """Create a sample armature for testing."""
    bl_idname = "blendin.create_sample_armature"
    bl_label = "Create Sample Armature"

    def execute(self, context):
        bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
        armature = context.object

        def create_bone(name, head, tail):
            bone = armature.data.edit_bones.new(name)
            bone.head = head
            bone.tail = tail

        create_bone("head", (0, 0, 1), (0, 0, 1.2))
        create_bone("neck", (0, 0, 0.8), (0, 0, 1))
        create_bone("hip", (0, 0, 0), (0, 0, 0.2))
        create_bone("left_shoulder", (0, 0, 0.8), (-0.2, 0, 0.8))
        create_bone("right_shoulder", (0, 0, 0.8), (0.2, 0, 0.8))

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BLENDIN_PT_main_panel)
    bpy.utils.register_class(BLENDIN_OT_create_sample_armature)


def unregister():
    bpy.utils.unregister_class(BLENDIN_PT_main_panel)
    bpy.utils.unregister_class(BLENDIN_OT_create_sample_armature)
