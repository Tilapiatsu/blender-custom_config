from mathutils import Matrix, Vector
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.types import Menu
import bpy

bl_info = {
    "name": "Pie UV",
    "description": "",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "doc_url": "",
    "category": "Pie Menu"
}


class TILA_MT_pie_uv(Menu):
    bl_idname = "TILA_MT_pie_uv"
    bl_label = "UV"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        pie = layout.menu_pie()

        if context.mode == "EDIT_MESH":
            pie.operator("mesh.mark_seam", icon='ADD', text='Mark Seam')
            pie.operator("mesh.mark_seam", icon='REMOVE', text="Clear Seam").clear=True
            pie.operator('uv.unwrap', icon='MOD_UVPROJECT', text='Unwrap')


classes = (
    TILA_MT_pie_uv,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
