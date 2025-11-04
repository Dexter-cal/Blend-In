import bpy

class BlendInFacialMapping(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
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

def register():
    bpy.utils.register_class(BlendInFacialMapping)
    bpy.utils.register_class(BlendInProperties)
    bpy.types.Scene.blend_in_props = bpy.props.PointerProperty(type=BlendInProperties)

def unregister():
    del bpy.types.Scene.blend_in_props
    bpy.utils.unregister_class(BlendInProperties)
    bpy.utils.unregister_class(BlendInFacialMapping)
