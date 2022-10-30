import bpy
bl_info = {
    "name": "toggle_snapping",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_ToggleUseAutoMergeOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_snapping"
    bl_label = "TILA: Toggle Snapping"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.space_data.type in ['VIEW_3D']:
            bpy.context.scene.tool_settings.use_snap = not bpy.context.scene.tool_settings.use_snap
        elif context.space_data.type in ['IMAGE_EDITOR']:
            bpy.context.scene.tool_settings.use_snap_uv = not bpy.context.scene.tool_settings.use_snap_uv
        return {'FINISHED'}

classes = (TILA_ToggleUseAutoMergeOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
