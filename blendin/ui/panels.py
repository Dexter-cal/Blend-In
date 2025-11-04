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

class BLENDIN_OT_create_sample_armature(bpy.types.Operator):
    """Create a sample armature for testing."""
    bl_idname = "blendin.create_sample_armature"
    bl_label = "Create Sample Armature"

    def execute(self, context):
        bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        armature = context.object
        armature.name = "Armature"

        def create_bone(name, head, tail):
            bone = armature.data.edit_bones.new(name)
            bone.head = head
            bone.tail = tail

        create_bone("head", (0, 0, 1), (0, 0, 1.2))
        create_bone("neck", (0, 0, 0.8), (0, 0, 1))
        create_bone("hip", (0, 0, 0), (0, 0, 0.2))
        create_bone("spine", (0, 0, 0.2), (0, 0, 0.8))
        create_bone("left_shoulder", (0, 0, 0.8), (-0.2, 0, 0.8))
        create_bone("right_shoulder", (0, 0, 0.8), (0.2, 0, 0.8))

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class BLENDIN_OT_create_test_character(bpy.types.Operator):
    """Create a simple head mesh with blendshapes for testing."""
    bl_idname = "blendin.create_test_character"
    bl_label = "Create Test Character"

    def execute(self, context):
        # ... (omitted for brevity)
        return {'FINISHED'}

class BLENDIN_OT_save_animation(bpy.types.Operator):
    bl_idname = "blendin.save_animation"
    bl_label = "Save Animation to Library"

    anim_name: bpy.props.StringProperty()
    anim_tags: bpy.props.StringProperty()

    def execute(self, context):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE' and armature.animation_data:
            motion_db.save_animation(self.anim_name, self.anim_tags, armature.animation_data.action)
            return {'FINISHED'}
        self.report({'ERROR'}, "Select an armature with an action.")
        return {'CANCELLED'}

class BLENDIN_OT_load_animation(bpy.types.Operator):
    bl_idname = "blendin.load_animation"
    bl_label = "Load Animation from Library"

    anim_id: bpy.props.IntProperty()

    def execute(self, context):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            motion_db.load_animation(self.anim_id, armature)
            return {'FINISHED'}
        self.report({'ERROR'}, "Select an armature to load the animation onto.")
        return {'CANCELLED'}

class BLENDIN_OT_delete_animation(bpy.types.Operator):
    bl_idname = "blendin.delete_animation"
    bl_label = "Delete Animation from Library"

    anim_id: bpy.props.IntProperty()

    def execute(self, context):
        motion_db.delete_animation(self.anim_id)
        return {'FINISHED'}

class BLENDIN_OT_export_fbx(bpy.types.Operator):
    bl_idname = "blendin.export_fbx"
    bl_label = "Export to FBX"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.filepath:
            self.filepath = "export.fbx"
        bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection=True)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BLENDIN_OT_export_gltf(bpy.types.Operator):
    bl_idname = "blendin.export_gltf"
    bl_label = "Export to glTF"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.filepath:
            self.filepath = "export.gltf"
        bpy.ops.export_scene.gltf(filepath=self.filepath, use_selection=True)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(BLENDIN_PT_main_panel)
    bpy.utils.register_class(BLENDIN_PT_rigging_panel)
    bpy.utils.register_class(BLENDIN_PT_motion_dna_panel)
    bpy.utils.register_class(BLENDIN_PT_export_panel)
    bpy.utils.register_class(BLENDIN_PT_facial_mapping_panel)
    bpy.utils.register_class(BLENDIN_OT_create_sample_armature)
    bpy.utils.register_class(BLENDIN_OT_create_test_character)
    bpy.utils.register_class(BLENDIN_OT_save_animation)
    bpy.utils.register_class(BLENDIN_OT_load_animation)
    bpy.utils.register_class(BLENDIN_OT_delete_animation)
    bpy.utils.register_class(BLENDIN_OT_export_fbx)
    bpy.utils.register_class(BLENDIN_OT_export_gltf)

def unregister():
    bpy.utils.unregister_class(BLENDIN_PT_main_panel)
    bpy.utils.unregister_class(BLENDIN_PT_rigging_panel)
    bpy.utils.unregister_class(BLENDIN_PT_motion_dna_panel)
    bpy.utils.unregister_class(BLENDIN_PT_export_panel)
    bpy.utils.unregister_class(BLENDIN_PT_facial_mapping_panel)
    bpy.utils.unregister_class(BLENDIN_OT_create_sample_armature)
    bpy.utils.unregister_class(BLENDIN_OT_create_test_character)
    bpy.utils.unregister_class(BLENDIN_OT_save_animation)
    bpy.utils.unregister_class(BLENDIN_OT_load_animation)
    bpy.utils.unregister_class(BLENDIN_OT_delete_animation)
    bpy.utils.unregister_class(BLENDIN_OT_export_fbx)
    bpy.utils.unregister_class(BLENDIN_OT_export_gltf)
