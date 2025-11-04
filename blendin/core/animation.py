import bpy
from ..comms.websocket_client import get_client
from .facial_mapping import FacialMapper
from .smoothing import SmoothingFilter

class LiveAnimationOperator(bpy.types.Operator):
    """Operator which runs a modal timer to update an armature and face."""
    bl_idname = "wm.live_animation_operator"
    bl_label = "Live Animation Operator"

    _timer = None
    _facial_mapper = None
    _smoothing_filter = None

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

                    # --- Skeletal Animation ---
                    if 'joints' in data:
                        armature = bpy.data.objects.get(props.target_armature)
                        if armature and armature.mode == 'POSE':
                            for joint in data['joints']:
                                bone_name = joint.get("name")
                                pose_bone = armature.pose.bones.get(bone_name)
                                if pose_bone:
                                    rotation = joint.get("rotation")
                                    if rotation and len(rotation) == 4:
                                        if pose_bone.rotation_mode != 'QUATERNION':
                                            pose_bone.rotation_mode = 'QUATERNION'

                                        pose_bone.rotation_quaternion = rotation

                                        if props.is_recording:
                                            pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=context.scene.frame_current)

                    # --- Facial Animation ---
                    if 'facial_landmarks' in data:
                        target_mesh = bpy.data.objects.get(props.target_mesh)
                        if self._facial_mapper is None or self.mappings_changed(props.facial_mappings):
                            mapping_config = {
                                m.name: {"upper": m.upper_landmark, "lower": m.lower_landmark}
                                for m in props.facial_mappings
                            }
                            self._facial_mapper = FacialMapper(mapping_config)

                        self._facial_mapper.update_blendshapes(target_mesh, data['facial_landmarks'])

                    # --- Vocal Animation ---
                    if 'vocal_energy' in data:
                        target_mesh = bpy.data.objects.get(props.target_mesh)
                        if target_mesh and target_mesh.data.shape_keys:
                            jaw_open_bs = target_mesh.data.shape_keys.key_blocks.get("jaw_open")
                            if jaw_open_bs:
                                jaw_open_bs.value = data['vocal_energy']


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
        target_armature_name = context.scene.blend_in_props.target_armature
        target_mesh_name = context.scene.blend_in_props.target_mesh

        if not target_armature_name and not target_mesh_name:
            self.report({'ERROR'}, "Please select a target armature or mesh.")
            return {'CANCELLED'}

        if target_armature_name and bpy.data.objects.get(target_armature_name):
            bpy.ops.object.mode_set(mode='POSE')

        wm = context.window_manager
        self._timer = wm.event_timer_add(1/60, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        return {'CANCELLED'}

def register():
    bpy.utils.register_class(LiveAnimationOperator)

def unregister():
    bpy.utils.unregister_class(LiveAnimationOperator)
