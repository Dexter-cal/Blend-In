import collections
import numpy as np
from mathutils import Quaternion

class SmoothingFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.joint_data = collections.defaultdict(lambda: collections.deque(maxlen=self.window_size))

    def smooth(self, data):
        if not data or 'joints' not in data:
            return data

        smoothed_joints = []
        for joint in data['joints']:
            joint_name = joint.get("name")
            rotation = joint.get("rotation")

            if joint_name and rotation:
                data_queue = self.joint_data[joint_name]
                data_queue.append(Quaternion(rotation))

                # Correct quaternion averaging using eigenvector method
                quats = np.array([list(q) for q in data_queue])
                M = quats.T @ quats
                _, v = np.linalg.eigh(M)
                avg_rotation = v[:, -1]

                smoothed_joints.append({"name": joint_name, "rotation": list(avg_rotation)})

        data["joints"] = smoothed_joints
        return data
