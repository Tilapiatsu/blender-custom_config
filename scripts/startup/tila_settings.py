import os
import addon_utils
import bpy
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


def register():
    pass


print("Loading Tilapiatu's user preferences")

# View Settings
bpy.context.preferences.view.show_tooltips = True
bpy.context.preferences.view.show_tooltips_python = True

# Edit Settings
bpy.context.preferences.edit.undo_steps = 200

# Input Settings
bpy.context.preferences.inputs.view_zoom_axis = "HORIZONTAL"
bpy.context.preferences.inputs.use_trackpad_natural = True
bpy.context.preferences.inputs.ndof_view_navigate_method = "FREE"
bpy.context.preferences.inputs.ndof_view_rotate_method = "TRACKBALL"
bpy.context.preferences.inputs.view_rotate_method = "TRACKBALL"
bpy.context.preferences.inputs.use_auto_perspective = True
bpy.context.preferences.inputs.use_mouse_depth_navigate = True
bpy.context.preferences.inputs.use_zoom_to_mouse = True

# Theme tweak
ui = bpy.context.preferences.themes[0]

ui.outliner.selected_highlight = (0.29, 0.38, 0.29)
ui.outliner.space.text = (0.6, 0.6, 0.6)
ui.outliner.space.text_hi = (0.733, 1.0, 0.584)


print("Loading Tilapiatu's user preferences Completed")
