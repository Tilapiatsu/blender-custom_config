import bpy
from .render_batcher import *

bl_info = {
    "name" : "Render_Batcher",
    "author" : "Tilapiatsu",
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Render"
}

classes = (render_batcher.RB_OP_RenderAllLayer)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()