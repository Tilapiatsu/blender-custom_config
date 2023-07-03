import sys
import importlib

import bpy
from bpy.app import handlers
from bpy.app.handlers import persistent

# Local imports implemented to support Blender refreshes
modulesNames = ("preferences",)
for module in modulesNames:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
    else:
        parent = ".".join(__name__.split(".")[:-1])
        globals()[module] = importlib.import_module(f"{parent}.{module}")


@persistent
def savePostHandler(_):
    prefs = preferences.get_user_preferences()
    if prefs.shouldDisplayPostSaveDialog and bpy.ops.cps.post_save_dialog.poll():
        bpy.ops.cps.post_save_dialog('INVOKE_DEFAULT')

    if prefs.shouldAutoStart:
        bpy.ops.cps.start_version_control('INVOKE_DEFAULT')


def register():
    handlers.save_post.append(savePostHandler)


def unregister():
    handlers.save_post.remove(savePostHandler)
