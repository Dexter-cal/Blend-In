import collections

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
            position = joint.get("position")

            if joint_name and position:
                data_queue = self.joint_data[joint_name]
                data_queue.append(position)

                # Calculate the average position
                avg_position = [sum(val) / len(data_queue) for val in zip(*data_queue)]
                smoothed_joints.append({"name": joint_name, "position": avg_position})

        return {"joints": smoothed_joints}
