from bpy.types import Menu
from .._ui import pcoll
from .._utils import get_prefs


class KePieSnapAlign(Menu):
    bl_label = "keSnapAlign"
    bl_idname = "VIEW3D_MT_ke_pie_align"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_modeling and k.m_selection

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.cursor_fit_selected_and_orient", text="Cursor Fit&Align", icon="ORIENTATION_CURSOR")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale H", icon="NODE_SIDE").screen_axis = 0

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Cursor", icon="CURSOR").orient_type = "CURSOR"

        pie.operator("mesh.ke_zeroscale", text="ZeroScale V", icon="NODE_TOP").screen_axis = 1

        c = pie.row()
        main = c.column()
        selbox = main.box().column()
        selbox.operator("view3d.snap_selected_to_grid", text="Selection to Grid", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.snap_selected_to_cursor", text="Selection to Cursor",
                        icon='RESTRICT_SELECT_OFF').use_offset = False
        selbox.operator("view3d.snap_selected_to_cursor", text="Sel.to Cursor w.Offset",
                        icon='RESTRICT_SELECT_OFF').use_offset = True
        selbox.operator("view3d.snap_selected_to_active", text="Selection to Active", icon='RESTRICT_SELECT_OFF')
        selbox.operator("view3d.selected_to_origin", text="Sel.to Origin (Set Origin)", icon='RESTRICT_SELECT_OFF')
        spacer = c.column()
        spacer.label(text="")
        main.label(text="")
        main.label(text="")

        pie.operator("mesh.ke_zeroscale", text="ZeroScale Normal", icon="NORMALS_FACE").orient_type = "NORMAL"

        c = pie.row()
        main = c.column()
        main.label(text="")
        main.label(text="")
        cbox = main.box().column()
        cbox.operator("view3d.snap_cursor_to_center", text="Cursor to World Origin", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_selected", text="Cursor to Selected", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_active", text="Cursor to Active", icon='CURSOR')
        cbox.operator("view3d.snap_cursor_to_grid", text="Cursor to Grid", icon='CURSOR')
        cbox.operator("view3d.ke_cursor_clear_rot", icon='CURSOR')
        spacer = c.column()
        spacer.label(text="")

        spacer = pie.row()
        spacer.label(text="")
        vbox = spacer.column()
        vbox.label(text="")
        vbox.label(text="")
        vbox = vbox.box().column()
        vbox.operator('view3d.align_origin_to_selected', text="Align Origin To Selected", icon="OBJECT_ORIGIN")
        vbox.operator('view3d.ke_origin_to_cursor', text="Align Origin(s) To Cursor", icon="PIVOT_CURSOR")
        vbox.operator('view3d.ke_object_to_cursor', text="Align Object(s) to Cursor", icon="CURSOR")
        vbox.operator('view3d.ke_align_object_to_active', text="Align Object(s) to Active", icon="CON_LOCLIKE")
        vbox.operator('view3d.ke_swap', text="Swap Places", icon="CON_TRANSLIKE")


class KePieSnapping(Menu):
    bl_label = "keSnapping"
    bl_idname = "VIEW3D_MT_ke_pie_snapping"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return context.space_data.type == "VIEW_3D" and k.m_bookmarks

    def draw(self, context):
        k = get_prefs()
        ct = context.scene.tool_settings
        name1 = k.snap_name1
        name2 = k.snap_name2
        name3 = k.snap_name3
        name4 = k.snap_name4
        name5 = k.snap_name5
        name6 = k.snap_name6
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id

        layout = self.layout
        pie = layout.menu_pie()

        # W
        pie.operator("view3d.ke_snap_combo", icon_value=s5, text="%s" % name5).mode = "SET5"
        # E
        pie.operator("view3d.ke_snap_combo", icon_value=s3, text="%s" % name3).mode = "SET3"
        # S
        pie.operator("view3d.ke_snap_combo", icon_value=s4, text="%s" % name4).mode = "SET4"
        # N
        pie.operator("view3d.ke_snap_combo", icon_value=s1, text="%s" % name1).mode = "SET1"
        # NW
        pie.operator("view3d.ke_snap_combo", icon_value=s6, text="%s" % name6).mode = "SET6"
        # NE
        pie.operator("view3d.ke_snap_combo", icon_value=s2, text="%s" % name2).mode = "SET2"

        # SW
        c = pie.column()
        c.separator(factor=18)
        c.ui_units_x = 9
        c.scale_y = 1.15
        cr = c.row()
        cbox = cr.box().column(align=True)
        cbox.prop(ct, 'snap_elements', expand=True)
        cbox.separator(factor=0.5)
        crow = cbox.grid_flow(align=True)
        crow.prop(ct, 'snap_target', expand=True)
        cr.separator(factor=2.5)

        # SE
        c = pie.row()
        c.separator(factor=2.5)
        c.ui_units_x = 9
        c.scale_y = 1.15
        r = c.column()
        r.separator(factor=18)
        cbox = r.box().row(align=True)
        cbox.prop(ct, 'use_snap', text="Snapping")
        cbox.prop(k, "combo_autosnap", text="Auto")
        r.separator(factor=1.25)
        cbox = r.box().column()
        cbox.scale_y = 1.06
        if not ct.use_snap_grid_absolute:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=False).op = "GRID"
        else:
            cbox.operator("ke.pieops", text="Absolute Grid", icon="SNAP_GRID", depress=True).op = "GRID"
        cbox.prop(ct, 'use_snap_align_rotation', text="Align Rotation")
        cbox.prop(ct, 'use_snap_self', text="Project Onto Self")
        cbox.prop(ct, 'use_snap_project', text="Project Ind.Elements")
        cbox.prop(ct, 'use_snap_backface_culling', text="Backface Culling")
        cbox.prop(ct, 'use_snap_peel_object', text="Peel Object")
        # cbox.separator(factor=0.5)
        row = cbox.row(align=True)
        row.prop(ct, 'use_snap_translate', text="T")
        row.prop(ct, 'use_snap_rotate', text="R")
        row.prop(ct, 'use_snap_scale', text="S")
