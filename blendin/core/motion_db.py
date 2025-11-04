import bpy
import sqlite3
import json
import os

def get_db_path():
    # Store the database in Blender's user data directory for persistence
    return os.path.join(bpy.utils.user_resource('DATAFILES'), "blendin_motion.db")

def init_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tags TEXT,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_animation(name, tags, action):
    if not action:
        return False

    animation_data = {}
    for fcurve in action.fcurves:
        bone_path = fcurve.data_path
        if bone_path not in animation_data:
            animation_data[bone_path] = []

        keyframes = []
        for key in fcurve.keyframe_points:
            keyframes.append((key.co.x, key.co.y))

        animation_data[bone_path].append({
            'array_index': fcurve.array_index,
            'keyframes': keyframes
        })

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO animations (name, tags, data) VALUES (?, ?, ?)",
        (name, tags, json.dumps(animation_data))
    )
    conn.commit()
    conn.close()
    return True

def load_animation(anim_id, armature_obj):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT name, data FROM animations WHERE id = ?", (anim_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return False

    anim_name, anim_data_json = result
    anim_data = json.loads(anim_data_json)

    # Create a new action
    if not armature_obj.animation_data:
        armature_obj.animation_data_create()

    action = bpy.data.actions.new(name=anim_name)
    armature_obj.animation_data.action = action

    # Apply the keyframes
    for bone_path, fcurves_data in anim_data.items():
        for fcurve_data in fcurves_data:
            fcurve = action.fcurves.new(data_path=bone_path, index=fcurve_data['array_index'])
            for frame, value in fcurve_data['keyframes']:
                fcurve.keyframe_points.insert(frame, value)

    return True


def list_animations():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, tags FROM animations")
    animations = cursor.fetchall()
    conn.close()
    return animations

def delete_animation(anim_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM animations WHERE id = ?", (anim_id,))
    conn.commit()
    conn.close()

# Ensure the database is initialized when the module is loaded
init_db()
