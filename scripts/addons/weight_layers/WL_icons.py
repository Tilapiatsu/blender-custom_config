import bpy
import os
from .WL_constants import CUSTOM_ICON_PATH

icon_groups = {}

def register():
    # register previews
    if not icon_groups:

        # custom icons
        pcoll = bpy.utils.previews.new()
        path = CUSTOM_ICON_PATH
        for file in os.listdir(path):
            if any([file.endswith(suffix) for suffix in [".png", ".svg"]]):
                icon_path = os.path.join(path, file)
                pcoll.load(file, icon_path, "IMAGE")
        icon_groups["wl_icons"] = pcoll

def unregister():
    # unregister icons
    for pcoll in icon_groups.values():
        bpy.utils.previews.remove(pcoll)
    icon_groups.clear()
