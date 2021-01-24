import bpy
bl_info = {
    "name": "toggle_use_automerge",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class TILA_ToggleUseAutoMergeOperator(bpy.types.Operator):
    bl_idname = "mesh.toggle_use_automerge"
    bl_label = "TILA: Toggle Use Automerge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.use_mesh_automerge = not bpy.context.scene.tool_settings.use_mesh_automerge
        return {'FINISHED'}

classes = (TILA_ToggleUseAutoMergeOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
