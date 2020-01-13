import bpy
bl_info = {
    "name": "toggle_snapping",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class ToggleUseAutoMergeOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_snapping"
    bl_label = "TILA: Toggle Snapping"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = not bpy.context.scene.tool_settings.use_snap
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
