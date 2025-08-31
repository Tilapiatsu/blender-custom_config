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


class TILA_uv_straighten_and_relax(bpy.types.Operator):
    bl_idname = "uv.tila_uv_straighten_and_relax"
    bl_label = "TILA: Straighten and Relax UV"

    straighten : bpy.props.BoolProperty(name="Straighten", default=True)
    relax : bpy.props.BoolProperty(name="Relax", default=True)
    align_to_nearest_axis : bpy.props.BoolProperty(name="Align", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if self.relax:
            bpy.ops.gret.relax_loops('EXEC_DEFAULT')
        if self.straighten:
            bpy.ops.uv.toolkit_distribute('EXEC_DEFAULT', preserve_edge_length=True, align_to_nearest_axis=self.align_to_nearest_axis)
        return {'FINISHED'}


classes = (
    TILA_uv_straighten_and_relax,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
