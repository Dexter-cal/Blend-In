import collections
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

                # Simple linear interpolation for quaternions.
                # A more advanced solution would use Slerp.
                avg_rotation = Quaternion()
                for q in data_queue:
                    avg_rotation.slerp(q, 1.0 / len(data_queue))

                smoothed_joints.append({"name": joint_name, "rotation": list(avg_rotation)})

        data["joints"] = smoothed_joints
        return data
