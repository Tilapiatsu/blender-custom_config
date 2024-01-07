import bpy
from bpy.types import (
    Operator,
)

#region dummy

class SRS_OT_Dummy(Operator):
    bl_label = "Dummy Operator"
    bl_idname = "superrealsound.dummy_operator"

    def execute(self, context):
        settings = bpy.context.scene.srs_settings

        self.report({'INFO'}, "Dummy Operator")
        return {'FINISHED'}

#endregion dummy

classes = (
    SRS_OT_Dummy,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")
