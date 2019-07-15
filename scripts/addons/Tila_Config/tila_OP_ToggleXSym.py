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
    bl_label = "TILA: Toggle X Symetry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode == 'SCULPT':
            context.scene.tool_settings.sculpt.use_symmetry_x = not context.scene.tool_settings.sculpt.use_symmetry_x
            self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.scene.tool_settings.sculpt.use_symmetry_x else 'OFF'))
        elif context.mode == 'EDIT_MESH':
            context.object.data.use_mirror_x = not context.object.data.use_mirror_x
            self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.object.data.use_mirror_x else 'OFF'))
        elif context.mode == 'PAINT_WEIGHT':
            context.object.data.use_mirror_x = not context.object.data.use_mirror_x
            self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.object.data.use_mirror_x else 'OFF'))
        elif context.mode == 'PAINT_VERTEX':
            context.scene.tool_settings.vertex_paint.use_symmetry_x = not context.scene.tool_settings.vertex_paint.use_symmetry_x
            self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.scene.tool_settings.vertex_paint.use_symmetry_x else 'OFF'))
        elif context.mode == 'PAINT_TEXTURE':
            context.scene.tool_settings.image_paint.use_symmetry_x = not context.scene.tool_settings.image_paint.use_symmetry_x
            self.report({'INFO'}, 'X Symetry {}'.format('ON' if context.scene.tool_settings.image_paint.use_symmetry_x else 'OFF'))
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
