from bpy.types import Menu
from .._utils import get_prefs
from .._ui import pcoll


class KePieOrientPivot(Menu):
    bl_label = "keOrientPivot"
    bl_idname = "VIEW3D_MT_ke_pie_orientpivot"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_bookmarks

    def draw(self, context):
        k = get_prefs()
        ct = context.scene.tool_settings
        name1 = k.opc1_name
        name2 = k.opc2_name
        name3 = k.opc3_name
        name4 = k.opc4_name
        name5 = k.opc5_name
        name6 = k.opc6_name

        mode = context.mode
        obj = context.active_object
        extmode = False
        if (obj is None) or (mode in {'OBJECT', 'POSE', 'WEIGHT_PAINT'}):
            extmode = True

        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.ke_opc", text="%s" % name5, icon_value=pcoll['kekit']['ke_opc5'].icon_id).combo = "5"
        pie.operator("view3d.ke_opc", text="%s" % name3, icon_value=pcoll['kekit']['ke_opc3'].icon_id).combo = "3"
        pie.operator("view3d.ke_opc", text="%s" % name4, icon_value=pcoll['kekit']['ke_opc4'].icon_id).combo = "4"
        pie.operator("view3d.ke_opc", text="%s" % name1, icon_value=pcoll['kekit']['ke_opc1'].icon_id).combo = "1"
        pie.operator("view3d.ke_opc", text="%s" % name6, icon_value=pcoll['kekit']['ke_opc6'].icon_id).combo = "6"
        pie.operator("view3d.ke_opc", text="%s" % name2, icon_value=pcoll['kekit']['ke_opc2'].icon_id).combo = "2"

        c = pie.column()
        c.separator(factor=13)
        cbox = c.box().column(align=True)
        cbox.scale_y = 1.2
        cbox.ui_units_x = 6.25
        cbox.prop(context.scene.transform_orientation_slots[0], "type", expand=True)

        c = pie.column()
        c.separator(factor=12.5)
        cbox = c.box().column(align=True)
        cbox.ui_units_x = 6.5
        cbox.scale_y = 1.3
        cbox.prop_enum(ct, "transform_pivot_point", value='BOUNDING_BOX_CENTER')
        cbox.prop_enum(ct, "transform_pivot_point", value='CURSOR')
        cbox.prop_enum(ct, "transform_pivot_point", value='INDIVIDUAL_ORIGINS')
        cbox.prop_enum(ct, "transform_pivot_point", value='MEDIAN_POINT')
        cbox.prop_enum(ct, "transform_pivot_point", value='ACTIVE_ELEMENT')
        if extmode:
            cbox = c.box().column(align=True)
            cbox.prop(ct, "use_transform_pivot_point_align")
        else:
            c.separator(factor=3)
