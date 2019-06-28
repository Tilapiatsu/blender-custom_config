import bpy
bl_info = {
    "name": "toggle_X_Symetry",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class ToggleXSymOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_x_symetry"
    bl_label = "TILA: Toggle Use Automerge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.use_symmetry_x = not bpy.context.scene.tool_settings.sculpt.use_symmetry_x
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
