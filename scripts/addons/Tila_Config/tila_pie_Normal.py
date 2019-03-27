from mathutils import Matrix
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.types import Menu
import bpy
bl_info = {
    "name": "Pie Normal",
    "description": "",
    "author": "Tilapiatsu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Pie Menu"
}


class TILA_MT_pie_normal(Menu):
    bl_idname = "TILA_MT_pie_normal"
    bl_label = "Normal"

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        obj = context.active_object
        pie = layout.menu_pie()
        # Left
        split = pie.split()
        col = split.column()
        col.scale_y = 1
        col.scale_x = 1.5
        if context.mode == "EDIT_MESH":
            if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                col.operator("view3d.tila_smoothnormal", icon='NODE_MATERIAL', text="Smooth")
            if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                col.operator("mesh.faces_shade_smooth", icon='NODE_MATERIAL', text="Smooth")
        elif context.mode == "OBJECT":
            col.operator("object.shade_smooth", icon='NODE_MATERIAL', text="Smooth")

        # Right
        split = pie.split()
        if context.mode == "EDIT_MESH":
            if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                col.operator("view3d.tila_splitnormal", icon='MESH_CUBE', text="Split")
            if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                col.operator("mesh.faces_shade_flat", icon='MESH_CUBE', text="Flat")
        elif context.mode == "OBJECT":
            col.operator("object.shade_flat", icon='MESH_CUBE', text="Flat")

        # Top
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("mesh.average_normals", icon='INVERSESQUARECURVE', text="Average Normal").average_type = 'FACE_AREA'

        # Bottom
        split = pie.split()
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="6").type = 'Cylinder_6'
        col = split.column()
        col.scale_y = 1.5
        col.scale_x = 1
        col.operator("view3d.hp_add_primitive", icon='MESH_CYLINDER', text="32").type = 'Cylinder_32'

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


class TILA_OT_autoSmooth(bpy.types.Operator):
    bl_idname = "view3d.tila_autosmooth"
    bl_label = "Tilapiatsu Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    value = bpy.props.BoolProperty(name='value', default=True)

    def execute(self, context):
        print('autosmooth')
        active = bpy.context.active_object

        if active:
            sel = bpy.context.selected_objects
            if active not in sel:
                sel.append(active)

            for obj in sel:
                obj.data.use_auto_smooth = self.value

        return {'FINISHED'}


class TILA_OT_splitNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_splitnormal"
    bl_label = "Tilapiatsu Split Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.split_normals()
        return {'FINISHED'}


class TILA_OT_smoothNormal(bpy.types.Operator):
    bl_idname = "view3d.tila_smoothnormal"
    bl_label = "Tilapiatsu Smooth Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.tila_autosmooth(value=True)
        bpy.ops.mesh.merge_normals()
        return {'FINISHED'}


classes = (
    TILA_MT_pie_normal,
    TILA_OT_autoSmooth
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
