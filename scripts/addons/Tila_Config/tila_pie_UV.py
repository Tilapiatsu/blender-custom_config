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
    "wiki_url": "",
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
        # Left
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        if context.mode == "EDIT_MESH":
            split.operator("mesh.mark_seam", icon='ADD', text='Mark Seam')

        # Right
        split = pie.split()
        split.scale_y = 3
        split.scale_x = 1.5
        if context.mode == "EDIT_MESH":
            split.operator("mesh.mark_seam", icon='REMOVE', text="Clear Seam").clear=True

        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1


        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1
        # if context.mode == "EDIT_MESH":
        #     col.operator('mesh.tila_normalflatten', icon='NORMALS_FACE', text='Flatten Normal')

        # Top Left

        split = pie.split()

        # Top Right
        split = pie.split()

        # Bottom Left

        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1

        # Bottom Right
        split = pie.split()
        col = split.column()
        col.scale_y = 3
        col.scale_x = 1

        # bpy.context.space_data.overlay.show_split_normals = True



classes = (
    TILA_MT_pie_uv
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
