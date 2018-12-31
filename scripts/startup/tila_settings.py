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

print("Loading Tilapiatu's user preferences")
bpy.types.PreferencesInput.items("view_zoom_axis") = "HORIZONTAL"
