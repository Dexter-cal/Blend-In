import bpy
from ..comms.websocket_client import get_client
from .smoothing import SmoothingFilter

class LiveAnimationOperator(bpy.types.Operator):
    """Operator which runs a modal timer to update an armature."""
    bl_idname = "wm.live_animation_operator"
    bl_label = "Live Animation Operator"

    _timer = None
    _smoothing_filter = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            client = get_client()
            if client:
                data = client.get_latest_data()

                if data and 'joints' in data:
                    armature = bpy.data.objects.get(context.scene.blend_in_props.target_armature)
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

                                    if context.scene.blend_in_props.is_recording:
                                        pose_bone.keyframe_insert(data_path="rotation_quaternion", frame=context.scene.frame_current)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        target_name = context.scene.blend_in_props.target_armature
        if not target_name or not bpy.data.objects.get(target_name):
            self.report({'ERROR'}, "Please select a target armature in the Blend-In panel.")
            return {'CANCELLED'}

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
