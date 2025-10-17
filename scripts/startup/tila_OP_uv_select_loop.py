import bpy

bl_info = {
    "name": "Tila : Straighten and Relax UV",
    "description": "This operator Relies on two other operators, one to straighten on UV Toolkit addon, and one to relax on Gret Addon",
    "author": ("Tilapiatsu"),
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View"
}


class TILA_uv_select(bpy.types.Operator):
    bl_idname = "uv.tila_uv_select"
    bl_label = "TILA: UV select"

    extend : bpy.props.BoolProperty(name="Extend", default=False)
    loop : bpy.props.BoolProperty(name="Loop", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        command = bpy.ops.uv.select
        if self.loop:
            command = bpy.ops.uv.select_loop

        command('INVOKE_DEFAULT', extend=self.extend)
        if self.loop and bpy.context.scene.tool_settings.uv_select_mode != 'VERTEX':
            command('INVOKE_DEFAULT', extend=self.extend)
        return {'FINISHED'}


classes = (
    TILA_uv_select,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
