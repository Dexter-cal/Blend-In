import bpy
from .core.retargeting import BoneMapping

class BlendInFacialMapping(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    baseline_distance: bpy.props.FloatProperty(
        name="Baseline Distance",
        description="The neutral distance between the landmarks for this blendshape",
        default=0.02,
        min=0.0,
        soft_max=0.2,
    )
    sensitivity: bpy.props.FloatProperty(
        name="Sensitivity",
        description="How sensitive the blendshape is to landmark movement",
        default=20.0,
        min=0.0,
        soft_max=100.0,
    )
    upper_landmark: bpy.props.EnumProperty(
        name="Upper Landmark",
        items=[
            ('lip_upper', 'Upper Lip', ''),
            ('lip_lower', 'Lower Lip', ''),
            ('eyebrow_left', 'Left Eyebrow', ''),
            ('eyebrow_right', 'Right Eyebrow', ''),
        ]
    )
    lower_landmark: bpy.props.EnumProperty(
        name="Lower Landmark",
        items=[
            ('lip_upper', 'Upper Lip', ''),
            ('lip_lower', 'Lower Lip', ''),
            ('eyebrow_left', 'Left Eyebrow', ''),
            ('eyebrow_right', 'Right Eyebrow', ''),
        ]
    )

def on_use_motion_debugger_update(self, context):
    from .core.motion_debugger import _motion_debugger, MotionDebugger
    if self.use_motion_debugger:
        if _motion_debugger is None:
            _motion_debugger = MotionDebugger()
        _motion_debugger.start()
    else:
        if _motion_debugger:
            _motion_debugger.stop()

class BlendInProperties(bpy.types.PropertyGroup):
    use_smoothing: bpy.props.BoolProperty(
        name="Use Smoothing",
        description="Apply a smoothing filter to the live animation data",
        default=False,
    )
    anim_name: bpy.props.StringProperty(
        name="Name",
        description="Name of the animation to save",
        default="New Animation",
    )
    anim_tags: bpy.props.StringProperty(
        name="Tags",
        description="Comma-separated tags for the animation",
        default="walk, run",
    )
    target_armature: bpy.props.StringProperty(
        name="Target Armature",
        description="The armature to apply the live animation to",
    )
    target_mesh: bpy.props.StringProperty(
        name="Target Mesh",
        description="The mesh with blendshapes to apply facial animation to",
    )
    is_recording: bpy.props.BoolProperty(
        name="Is Recording",
        description="Record the live animation to the timeline",
        default=False,
    )
    facial_mappings: bpy.props.CollectionProperty(type=BlendInFacialMapping)
    use_motion_textures: bpy.props.BoolProperty(
        name="Use Motion Textures",
        description="Apply generative idle motion to the character",
        default=False,
    )
    dream_prompt: bpy.props.StringProperty(
        name="Dream Prompt",
        description="Describe the pose you want to generate",
        default="A character who is sad",
    )
    bone_mappings: bpy.props.CollectionProperty(type=BoneMapping)
    use_motion_debugger: bpy.props.BoolProperty(
        name="Use Motion Debugger",
        description="Display real-time motion diagnostics in the viewport",
        default=False,
        update=on_use_motion_debugger_update,
    )


def register():
    bpy.utils.register_class(BoneMapping)
    bpy.utils.register_class(BlendInFacialMapping)
    bpy.utils.register_class(BlendInProperties)
    bpy.types.Scene.blend_in_props = bpy.props.PointerProperty(type=BlendInProperties)

def unregister():
    del bpy.types.Scene.blend_in_props
    bpy.utils.unregister_class(BlendInProperties)
    bpy.utils.unregister_class(BlendInFacialMapping)
    bpy.utils.unregister_class(BoneMapping)
