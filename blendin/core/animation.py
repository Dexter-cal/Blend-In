import bpy
import time
import math
from mathutils import Quaternion, Euler
from ..comms.websocket_client import get_client
from .facial_mapping import FacialMapper
from .smoothing import SmoothingFilter
from .motion_textures import MotionTextureGenerator
from .retargeting import apply_retargeting
from .motion_debugger import MotionDebugger, _motion_debugger

class LiveAnimationOperator(bpy.types.Operator):
    """Operator which runs a modal timer to update an armature and face."""
    bl_idname = "wm.live_animation_operator"
    bl_label = "Live Animation Operator"

    _timer = None
    _facial_mapper = None
    _smoothing_filter = None
    _motion_texture_generator = None
    _start_time = 0
    _armature = None
    _mesh = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            client = get_client()
            if client:
                data = client.get_latest_data()

                if data:
                    props = context.scene.blend_in_props

                    # --- Smoothing ---
                    if props.use_smoothing:
                        if self._smoothing_filter is None:
                            self._smoothing_filter = SmoothingFilter()
                        data = self._smoothing_filter.smooth(data)
                    else:
                        self._smoothing_filter = None

                    # --- Motion Textures ---
                    texture_offsets = {}
                    if props.use_motion_textures:
                        if self._motion_texture_generator is None:
                            self._motion_texture_generator = MotionTextureGenerator()

                        elapsed_time = time.time() - self._start_time
                        texture_offsets = self._motion_texture_generator.get_offsets(elapsed_time)

                    # --- Skeletal Animation ---
                    if 'joints' in data:
                        armature = self._armature

                        # Create a dictionary of source rotations
                        source_rotations = {
                            joint['name']: Quaternion(joint.get("rotation", [1, 0, 0, 0]))
                            for joint in data['joints']
                        }

                        # Apply retargeting
                        apply_retargeting(armature, source_rotations, props.bone_mappings)

                        # Apply motion textures
                        if armature and armature.mode == 'POSE':
                            for bone_name, offset in texture_offsets.items():
                                pose_bone = armature.pose.bones.get(bone_name)
                                if pose_bone:
                                    pose_bone.rotation_quaternion @= offset

                        # Record keyframes
                        if props.is_recording and armature and armature.mode == 'POSE':
                            for mapping in props.bone_mappings:
                                pose_bone = armature.pose.bones.get(mapping.target_bone)
                                if pose_bone:
                                    pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=context.scene.frame_current)


                    # --- Facial Animation ---
                    if 'facial_landmarks' in data:
                        target_mesh = self._mesh
                        if self._facial_mapper is None or self.mappings_changed(props.facial_mappings):
                            mapping_config = {
                                m.name: {
                                    "upper": m.upper_landmark,
                                    "lower": m.lower_landmark,
                                    "baseline": m.baseline_distance,
                                    "sensitivity": m.sensitivity,
                                }
                                for m in props.facial_mappings
                            }
                            self._facial_mapper = FacialMapper(mapping_config)

                        self._facial_mapper.update_blendshapes(target_mesh, data['facial_landmarks'])

                        if props.is_recording and target_mesh and target_mesh.data.shape_keys:
                            for mapping in props.facial_mappings:
                                blendshape = target_mesh.data.shape_keys.key_blocks.get(mapping.name)
                                if blendshape:
                                    blendshape.keyframe_insert(data_path="value", frame=context.scene.frame_current)

                    # --- Vocal Animation ---
                    if 'vocal_energy' in data:
                        target_mesh = self._mesh
                        if target_mesh and target_mesh.data.shape_keys:
                            jaw_open_bs = target_mesh.data.shape_keys.key_blocks.get("jaw_open")
                            if jaw_open_bs:
                                jaw_open_bs.value = data['vocal_energy']
                                if props.is_recording:
                                    jaw_open_bs.keyframe_insert(data_path="value", frame=context.scene.frame_current)

                    # --- Update Debugger ---
                    global _motion_debugger
                    if _motion_debugger:
                        _motion_debugger.update(self._armature)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def mappings_changed(self, new_mappings):
        if self._facial_mapper is None:
            return True
        # A simple check to see if the mapping config needs rebuilding
        current_config = self._facial_mapper.mapping_config
        if len(new_mappings) != len(current_config):
            return True
        for m in new_mappings:
            if m.name not in current_config or \
               current_config[m.name]['upper'] != m.upper_landmark or \
               current_config[m.name]['lower'] != m.lower_landmark:
                return True
        return False

    def execute(self, context):
        props = context.scene.blend_in_props
        self._armature = bpy.data.objects.get(props.target_armature)
        self._mesh = bpy.data.objects.get(props.target_mesh)

        if not self._armature and not self._mesh:
            self.report({'ERROR'}, "Please select a target armature or mesh.")
            return {'CANCELLED'}

        if self._armature:
            bpy.ops.object.mode_set(mode='POSE')

        wm = context.window_manager
        self._timer = wm.event_timer_add(1/60, window=context.window)
        wm.modal_handler_add(self)
        self._start_time = time.time()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)

        global _motion_debugger
        if _motion_debugger:
            _motion_debugger.stop()

        return {'CANCELLED'}

def register():
    bpy.utils.register_class(LiveAnimationOperator)

def unregister():
    bpy.utils.unregister_class(LiveAnimationOperator)
