from mathutils import Vector

def calculate_blendshape_value(landmarks, upper_landmark, lower_landmark, baseline_distance, sensitivity):
    """
    Calculates a blendshape value based on the vertical distance
    between two landmarks.
    """
    if not landmarks or upper_landmark not in landmarks or lower_landmark not in landmarks:
        return 0.0

    upper_pos = Vector(landmarks[upper_landmark])
    lower_pos = Vector(landmarks[lower_landmark])

    # Using the y-axis for vertical distance as a simple starting point
    distance = abs(upper_pos.y - lower_pos.y)

    value = (distance - baseline_distance) * sensitivity

    # Clamp the value between 0 and 1
    return max(0.0, min(1.0, value))

class FacialMapper:
    def __init__(self, mapping_config):
        self.mapping_config = mapping_config

    def update_blendshapes(self, target_mesh, landmarks):
        if not target_mesh or not target_mesh.data.shape_keys or not landmarks:
            return

        for blendshape_name, landmark_info in self.mapping_config.items():
            blendshape = target_mesh.data.shape_keys.key_blocks.get(blendshape_name)
            if blendshape:
                upper = landmark_info.get("upper")
                lower = landmark_info.get("lower")
                baseline = landmark_info.get("baseline", 0.02)
                sensitivity = landmark_info.get("sensitivity", 20.0)

                if upper and lower:
                    value = calculate_blendshape_value(landmarks, upper, lower, baseline, sensitivity)
                    blendshape.value = value
