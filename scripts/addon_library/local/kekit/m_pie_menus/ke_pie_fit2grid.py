from bpy.types import Menu
from .._utils import get_prefs


class KePieFit2Grid(Menu):
    bl_label = "keFit2Grid"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="50cm").set_grid = 0.5
        pie.operator("view3d.ke_fit2grid", text="5cm").set_grid = 0.05
        pie.operator("view3d.ke_fit2grid", text="15cm").set_grid = 0.15
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="1m").set_grid = 1.0
        pie.operator("view3d.ke_fit2grid", text="2.5cm").set_grid = 0.025
        pie.operator("view3d.ke_fit2grid", text="25cm").set_grid = 0.25
        pie.operator("view3d.ke_fit2grid", text="10cm").set_grid = 0.1


class KePieFit2GridMicro(Menu):
    bl_label = "keFit2Grid_micro"
    bl_idname = "VIEW3D_MT_ke_pie_fit2grid_micro"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_fit2grid", text="5mm").set_grid = 0.005
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1.5mm").set_grid = 0.0015
        pie.operator("view3d.ke_fit2grid", text="1µm").set_grid = 0.0001
        pie.operator("view3d.ke_fit2grid", text="1cm").set_grid = 0.01
        pie.operator("view3d.ke_fit2grid", text="2.5µm").set_grid = 0.00025
        pie.operator("view3d.ke_fit2grid", text="5µm").set_grid = 0.0005
        pie.operator("view3d.ke_fit2grid", text="1mm").set_grid = 0.001
