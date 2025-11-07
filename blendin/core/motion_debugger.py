import bpy
import gpu
from gpu_extras.batch import batch_for_shader

class MotionDebugger:
    """
    Draws real-time motion diagnostics in the 3D viewport.
    """
    def __init__(self):
        self.draw_handler = None
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.batch = None

    def start(self):
        if self.draw_handler is None:
            # Initialize with a dummy vertex
            self.batch = batch_for_shader(self.shader, 'POINTS', {"pos": [(0, 0, 0)]})
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (), 'WINDOW', 'POST_VIEW'
            )

    def stop(self):
        if self.draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
            self.batch = None

    def update(self, armature):
        """
        Updates the debugger with the latest armature state.
        For now, calculates and displays the center of mass.
        """
        if not armature or armature.mode != 'POSE' or not self.batch:
            return

        total_mass = 0
        com = [0, 0, 0]

        # A simple approximation: treat each bone as a point mass at its head
        for bone in armature.pose.bones:
            mass = 1.0 # Assume uniform mass for now
            total_mass += mass
            com[0] += bone.head[0] * mass
            com[1] += bone.head[1] * mass
            com[2] += bone.head[2] * mass

        if total_mass > 0:
            com[0] /= total_mass
            com[1] /= total_mass
            com[2] /= total_mass

        # Update the batch's vertex data
        self.batch.vert_set('pos', [tuple(com)])

    def draw(self):
        if self.batch:
            self.shader.bind()
            self.shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0)) # Yellow
            gpu.state.point_size_set(10)
            self.batch.draw(self.shader)
