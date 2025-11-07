import bpy
import bmesh
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
        row.prop_search(props, "target_mesh", bpy.data, "objects", text="Face Mesh")

        row = layout.row()
        row.prop(props, "use_smoothing")
        row = layout.row()
        row.prop(props, "use_motion_textures")
        row = layout.row()
        row.prop(props, "use_motion_debugger")

        row = layout.row()
        row.operator("wm.live_animation_operator", text="Start Live Preview")

        row = layout.row()
        row.prop(props, "is_recording", text="Record", toggle=True)

class BLENDIN_PT_rigging_panel(bpy.types.Panel):
    bl_label = "Rigging"
    bl_idname = "BLENDIN_PT_rigging_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("blendin.auto_rig", text="Auto-Rig Character")
        row = layout.row()
        row.operator("blendin.create_sample_armature", text="Create Sample Armature")
        row = layout.row()
        row.operator("blendin.create_test_character", text="Create Test Character")

class BLENDIN_PT_motion_dna_panel(bpy.types.Panel):
    bl_label = "Motion DNA Library"
    bl_idname = "BLENDIN_PT_motion_dna_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_in_props

        # Save Animation Section
        box = layout.box()
        box.label(text="Save Current Animation")
        row = box.row()
        row.prop(props, "anim_name")
        row = box.row()
        row.prop(props, "anim_tags")
        row = box.row()
        op = row.operator("blendin.save_animation", text="Save")
        op.anim_name = props.anim_name
        op.anim_tags = props.anim_tags

        # Library Section
        box = layout.box()
        box.label(text="Library")

        animations = motion_db.list_animations()
        for anim_id, name, tags in animations:
            row = box.row(align=True)
            row.label(text=f"{name} ({tags})")

            load_op = row.operator("blendin.load_animation", text="Load")
            load_op.anim_id = anim_id

            delete_op = row.operator("blendin.delete_animation", text="X")
            delete_op.anim_id = anim_id

class BLENDIN_PT_export_panel(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "BLENDIN_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("blendin.export_fbx", text="Export to FBX")
        row = layout.row()
        row.operator("blendin.export_gltf", text="Export to glTF")

class BLENDIN_PT_facial_mapping_panel(bpy.types.Panel):
    bl_label = "Facial Mapping"
    bl_idname = "BLENDIN_PT_facial_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_in_props

        target_obj = bpy.data.objects.get(props.target_mesh)

        if target_obj and target_obj.type == 'MESH' and target_obj.data.shape_keys:

            # Sync properties with shape keys
            if len(props.facial_mappings) != len([key for key in target_obj.data.shape_keys.key_blocks if key.name != "Basis"]):
                props.facial_mappings.clear()
                for key in target_obj.data.shape_keys.key_blocks:
                    if key.name != "Basis":
                        item = props.facial_mappings.add()
                        item.name = key.name

            for i, mapping in enumerate(props.facial_mappings):
                box = layout.box()
                row = box.row()
                row.label(text=mapping.name)
                row = box.row()
                row.prop(mapping, "upper_landmark", text="Upper")
                row = box.row()
                row.prop(mapping, "lower_landmark", text="Lower")
                row = box.row()
                row.prop(mapping, "baseline_distance", text="Baseline")
                row = box.row()
                row.prop(mapping, "sensitivity", text="Sensitivity")

class BLENDIN_PT_dream_capture_panel(bpy.types.Panel):
    bl_label = "Dream Capture"
    bl_idname = "BLENDIN_PT_dream_capture_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_in_props

        row = layout.row()
        row.prop(props, "dream_prompt", text="")

        row = layout.row()
        row.operator("blendin.generate_animation", text="Generate Animation")

class BLENDIN_PT_retargeting_panel(bpy.types.Panel):
    bl_label = "Retargeting"
    bl_idname = "BLENDIN_PT_retargeting_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'
    bl_parent_id = "BLENDIN_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    # Define the list of source bones from our data stream
    SOURCE_BONES = ["head", "neck", "hip", "spine", "left_shoulder", "right_shoulder"]

    def draw(self, context):
        layout = self.layout
        props = context.scene.blend_in_props
        armature = bpy.data.objects.get(props.target_armature)

        if not armature or armature.type != 'ARMATURE':
            layout.label(text="Select a target armature.")
            return

        # Sync the mapping properties with the source bones
        if len(props.bone_mappings) != len(self.SOURCE_BONES):
            props.bone_mappings.clear()
            for bone_name in self.SOURCE_BONES:
                item = props.bone_mappings.add()
                item.source_bone = bone_name

        # Draw the UI
        box = layout.box()
        for mapping in props.bone_mappings:
            row = box.row()
            row.label(text=mapping.source_bone)
            # Create a searchable dropdown of the target armature's bones
            row.prop_search(mapping, "target_bone", armature.data, "bones", text="")

def register():
    bpy.utils.register_class(BLENDIN_PT_main_panel)
    bpy.utils.register_class(BLENDIN_PT_rigging_panel)
    bpy.utils.register_class(BLENDIN_PT_motion_dna_panel)
    bpy.utils.register_class(BLENDIN_PT_export_panel)
    bpy.utils.register_class(BLENDIN_PT_facial_mapping_panel)
    bpy.utils.register_class(BLENDIN_PT_dream_capture_panel)
    bpy.utils.register_class(BLENDIN_PT_retargeting_panel)

def unregister():
    bpy.utils.unregister_class(BLENDIN_PT_main_panel)
    bpy.utils.unregister_class(BLENDIN_PT_rigging_panel)
    bpy.utils.unregister_class(BLENDIN_PT_motion_dna_panel)
    bpy.utils.unregister_class(BLENDIN_PT_export_panel)
    bpy.utils.unregister_class(BLENDIN_PT_facial_mapping_panel)
    bpy.utils.unregister_class(BLENDIN_PT_dream_capture_panel)
    bpy.utils.unregister_class(BLENDIN_PT_retargeting_panel)
