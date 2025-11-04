bl_info = {
    "name": "Blend-In",
    "author": "Jules",
    "version": (0, 1, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > Blend-In",
    "description": "Live AI rigging & capture",
    "category": "Animation",
}

import bpy
from .comms.websocket_client import start_client, stop_client, get_client
from .core import animation, rigging
from .ui import panels
from . import properties

def register():
    start_client()
    properties.register()
    animation.register()
    rigging.register()
    panels.register()
    print("Blend-In addon registered.")

def unregister():
    stop_client()
    properties.unregister()
    animation.unregister()
    rigging.unregister()
    panels.unregister()
    print("Blend-In addon unregistered.")
