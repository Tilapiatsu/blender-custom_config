bl_info = {
            "name": "Tilapiatsu Settings",
            "description": "Settings",
            "author": "Tilapiatsu",
            "version": (0, 1, 0),
            "blender": (2, 80, 0),
            "location": "",
            "warning": "",
            "wiki_url": "",
            "category": "Settings"
            }

import bpy
import os

def register():
    pass

print("Loading Tilapiatu's user preferences")

# View Settings
bpy.context.preferences.view.show_tooltips = True
bpy.context.preferences.view.show_tooltips_python = True
bpy.context.preferences.view.use_auto_perspective = True
bpy.context.preferences.view.use_mouse_depth_navigate = True
bpy.context.preferences.view.use_zoom_to_mouse = True

# Edit Settings
bpy.context.preferences.edit.undo_steps = 200

# Input Settings
bpy.context.preferences.inputs.view_zoom_axis = "HORIZONTAL"
bpy.context.preferences.inputs.use_trackpad_natural = True
bpy.context.preferences.inputs.ndof_view_navigate_method = "FREE"
bpy.context.preferences.inputs.ndof_view_rotate_method = "TRACKBALL"
bpy.context.preferences.inputs.view_rotate_method = "TRACKBALL"

print("Loading Tilapiatu's user preferences Completed")