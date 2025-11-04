import bpy
from ..core import motion_db

class BLENDIN_PT_main_panel(bpy.types.Panel):
    bl_label = "Blend-In"
    bl_idname = "BLENDIN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Live Capture")
        props = context.scene.blend_in_props

        row = layout.row()
        row.prop_search(props, "target_armature", bpy.data, "objects", text="Target")

        row = layout.row()
        row.prop(props, "use_smoothing")

        row = layout.row()
        row.operator("wm.live_animation_operator", text="Start Live Preview")

        row = layout.row()
        row.prop(props, "is_recording", text="Record", toggle=True)


class BLENDIN_PT_rigging_panel(bpy.types.Panel):
    # ... (omitted for brevity)
    pass
# ... (rest of the file is the same)
