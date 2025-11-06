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
import sys
import subprocess

# --- Dependency Management ---

try:
    import websockets
    import numpy
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

class BLENDIN_OT_install_dependencies(bpy.types.Operator):
    bl_idname = "blendin.install_dependencies"
    bl_label = "Install Dependencies"

    def execute(self, context):
        try:
            py_exec = sys.executable
            subprocess.check_call([py_exec, "-m", "pip", "install", "websockets", "numpy"])
            global DEPENDENCIES_AVAILABLE
            DEPENDENCIES_AVAILABLE = True
            self.report({'INFO'}, "Dependencies installed. Please re-enable the addon.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to install dependencies: {e}")
        return {'FINISHED'}

class BLENDIN_PT_dependency_panel(bpy.types.Panel):
    bl_label = "Blend-In"
    bl_idname = "BLENDIN_PT_dependency_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blend-In'

    def draw(self, context):
        self.layout.label(text="Dependencies not installed.")
        self.layout.operator("blendin.install_dependencies")

# --- Addon Registration ---

from . import properties
from .core import animation, rigging
from .ui import panels

def register():
    bpy.utils.register_class(BLENDIN_OT_install_dependencies)
    bpy.utils.register_class(BLENDIN_PT_dependency_panel)

    if DEPENDENCIES_AVAILABLE:
        properties.register()
        animation.register()
        rigging.register()
        panels.register()
        print("Blend-In addon registered.")

def unregister():
    bpy.utils.unregister_class(BLENDIN_OT_install_dependencies)
    bpy.utils.unregister_class(BLENDIN_PT_dependency_panel)

    if DEPENDENCIES_AVAILABLE:
        properties.unregister()
        animation.unregister()
        rigging.unregister()
        panels.unregister()
        print("Blend-In addon unregistered.")
