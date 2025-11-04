import bpy
from ..comms.websocket_client import get_client

class LiveAnimationOperator(bpy.types.Operator):
    """Operator which runs a modal timer to update an armature."""
    bl_idname = "wm.live_animation_operator"
    bl_label = "Live Animation Operator"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            client = get_client()
            if client:
                data = client.get_latest_data()
                if data and 'joints' in data:
                    armature = bpy.data.objects.get("Armature")
                    if armature:
                        for joint in data['joints']:
                            bone_name = joint.get("name")
                            pose_bone = armature.pose.bones.get(bone_name)
                            if pose_bone:
                                position = joint.get("position")
                                if position:
                                    # We'll use location for now, but will likely switch to rotation
                                    pose_bone.location = position

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/60, window=context.window) # 60fps
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

def register():
    bpy.utils.register_class(LiveAnimationOperator)

def unregister():
    bpy.utils.unregister_class(LiveAnimationOperator)
