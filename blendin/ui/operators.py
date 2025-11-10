import bpy
from mathutils import Vector
import bmesh
from ..core import motion_db
from ..core.dream_capture import DreamCapture
from ..comms import websocket_client

class BLENDIN_OT_connect_toggle(bpy.types.Operator):
    bl_idname = "blendin.connect_toggle"
    bl_label = "Connect/Disconnect WebSocket"

    def execute(self, context):
        props = context.scene.blend_in_props
        if props.is_connected:
            # Disconnect
            websocket_client.stop_client()
            props.is_connected = False
            self.report({'INFO'}, "Disconnected from WebSocket server.")
        else:
            # Connect
            success = websocket_client.start_client(props.websocket_host, props.websocket_port)
            if success:
                props.is_connected = True
                self.report({'INFO'}, f"Connecting to ws://{props.websocket_host}:{props.websocket_port}")
            else:
                props.is_connected = False
                self.report({'ERROR'}, "Failed to connect to WebSocket server.")
        return {'FINISHED'}

class BLENDIN_OT_create_sample_armature(bpy.types.Operator):
    bl_idname = "blendin.create_sample_armature"
    bl_label = "Create Sample Armature"

    def execute(self, context):
        # Create a new armature
        bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
        armature_obj = context.view_layer.objects.active
        armature_obj.name = "Sample_Rig"
        edit_bones = armature_obj.data.edit_bones

        # Define bone structure
        bone_defs = {
            "hip": ((0, 0, 1), (0, 0, 1.1)),
            "spine": ((0, 0, 1.1), (0, 0, 1.5)),
            "neck": ((0, 0, 1.5), (0, 0, 1.6)),
            "head": ((0, 0, 1.6), (0, 0, 1.8)),
            "left_shoulder": ((0.1, 0, 1.5), (0.2, 0, 1.5)),
            "right_shoulder": ((-0.1, 0, 1.5), (-0.2, 0, 1.5)),
        }

        parent_map = {
            "spine": "hip",
            "neck": "spine",
            "head": "neck",
            "left_shoulder": "spine",
            "right_shoulder": "spine",
        }

        # Create bones
        for name, (head, tail) in bone_defs.items():
            bone = edit_bones.new(name)
            bone.head = head
            bone.tail = tail

        # Parent bones
        for child, parent in parent_map.items():
            edit_bones[child].parent = edit_bones[parent]

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class BLENDIN_OT_create_test_character(bpy.types.Operator):
    bl_idname = "blendin.create_test_character"
    bl_label = "Create Test Character"

    def execute(self, context):
        # Create a simple mesh
        bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.8, location=(0, 0, 0.9))
        mesh_obj = context.view_layer.objects.active
        mesh_obj.name = "Test_Character_Mesh"

        # Create a sample armature
        bpy.ops.blendin.create_sample_armature()
        armature_obj = context.view_layer.objects.active

        # Parent mesh to armature
        mesh_obj.parent = armature_obj
        modifier = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
        modifier.object = armature_obj

        # Add a "jaw_open" blendshape
        mesh_obj.shape_key_add(name="Basis")
        jaw_open_shape_key = mesh_obj.shape_key_add(name="jaw_open")

        # Deform the mesh for the jaw_open shape key
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(mesh_obj.data)
        jaw_verts = [v for v in bm.verts if v.co.z < 0.2 and v.co.y > 0]
        for v in jaw_verts:
            jaw_open_shape_key.data[v.index].co.z -= 0.1
        bmesh.update_edit_mesh(mesh_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class BLENDIN_OT_save_animation(bpy.types.Operator):
    bl_idname = "blendin.save_animation"
    bl_label = "Save Animation to Library"
    anim_name: bpy.props.StringProperty()
    anim_tags: bpy.props.StringProperty()

    def execute(self, context):
        armature = bpy.data.objects.get(context.scene.blend_in_props.target_armature)
        if not armature or not armature.animation_data or not armature.animation_data.action:
            self.report({'ERROR'}, "No active animation to save.")
            return {'CANCELLED'}

        motion_db.save_animation(self.anim_name, self.anim_tags, armature.animation_data.action)
        self.report({'INFO'}, f"Animation '{self.anim_name}' saved.")
        return {'FINISHED'}


class BLENDIN_OT_load_animation(bpy.types.Operator):
    bl_idname = "blendin.load_animation"
    bl_label = "Load Animation from Library"
    anim_id: bpy.props.IntProperty()

    def execute(self, context):
        armature = bpy.data.objects.get(context.scene.blend_in_props.target_armature)
        if not armature:
            self.report({'ERROR'}, "Select a target armature first.")
            return {'CANCELLED'}

        motion_db.load_animation(self.anim_id, armature)
        self.report({'INFO'}, "Animation loaded.")
        return {'FINISHED'}

class BLENDIN_OT_delete_animation(bpy.types.Operator):
    bl_idname = "blendin.delete_animation"
    bl_label = "Delete Animation from Library"
    anim_id: bpy.props.IntProperty()

    def execute(self, context):
        motion_db.delete_animation(self.anim_id)
        self.report({'INFO'}, "Animation deleted.")
        return {'FINISHED'}

class BLENDIN_OT_export_fbx(bpy.types.Operator):
    bl_idname = "blendin.export_fbx"
    bl_label = "Export to FBX"

    def execute(self, context):
        # This is a placeholder for a more complete export operator
        self.report({'INFO'}, "Exporting to FBX...")
        return {'FINISHED'}

class BLENDIN_OT_export_gltf(bpy.types.Operator):
    bl_idname = "blendin.export_gltf"
    bl_label = "Export to glTF"

    def execute(self, context):
        # This is a placeholder for a more complete export operator
        self.report({'INFO'}, "Exporting to glTF...")
        return {'FINISHED'}

class BLENDIN_OT_generate_animation(bpy.types.Operator):
    bl_idname = "blendin.generate_animation"
    bl_label = "Generate Animation from Prompt"

    def execute(self, context):
        props = context.scene.blend_in_props
        armature = bpy.data.objects.get(props.target_armature)

        if not armature:
            self.report({'ERROR'}, "Please select a target armature.")
            return {'CANCELLED'}

        if armature.mode != 'POSE':
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')

        dream_capture = DreamCapture()
        animation_data = dream_capture.get_animation_for_prompt(props.dream_prompt)

        if animation_data:
            dream_capture.apply_animation_to_armature(armature, animation_data)
        else:
            self.report({'WARNING'}, f"No animation found for prompt: {props.dream_prompt}")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(BLENDIN_OT_connect_toggle)
    bpy.utils.register_class(BLENDIN_OT_create_sample_armature)
    bpy.utils.register_class(BLENDIN_OT_create_test_character)
    bpy.utils.register_class(BLENDIN_OT_save_animation)
    bpy.utils.register_class(BLENDIN_OT_load_animation)
    bpy.utils.register_class(BLENDIN_OT_delete_animation)
    bpy.utils.register_class(BLENDIN_OT_export_fbx)
    bpy.utils.register_class(BLENDIN_OT_export_gltf)
    bpy.utils.register_class(BLENDIN_OT_generate_animation)

def unregister():
    bpy.utils.unregister_class(BLENDIN_OT_connect_toggle)
    bpy.utils.unregister_class(BLENDIN_OT_create_sample_armature)
    bpy.utils.unregister_class(BLENDIN_OT_create_test_character)
    bpy.utils.unregister_class(BLENDIN_OT_save_animation)
    bpy.utils.unregister_class(BLENDIN_OT_load_animation)
    bpy.utils.unregister_class(BLENDIN_OT_delete_animation)
    bpy.utils.unregister_class(BLENDIN_OT_export_fbx)
    bpy.utils.unregister_class(BLENDIN_OT_export_gltf)
    bpy.utils.unregister_class(BLENDIN_OT_generate_animation)
