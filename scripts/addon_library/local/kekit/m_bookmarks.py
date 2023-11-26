import bpy
from bpy.types import Panel

from .ops.ke_cursor_bookmark import KeCursorBookmarks
from .ops.ke_opc import KeOPC
from .ops.ke_snapcombo import KeSnapCombo
from .ops.ke_view_bookmark import KeViewBookmark
from .ops.ke_view_bookmark_cycle import KeViewBookmarkCycle
from .ops.ke_view_pos import KeViewPos

from ._utils import get_prefs
from ._ui import pcoll


class UIBookmarksModule(Panel):
    bl_idname = "UI_PT_M_BOOKMARKS"
    bl_label = "Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    info_cursor = "Store & Recall Cursor Transforms (loc & rot)\n" \
                  "Clear Slot: Reset cursor (zero loc & rot) and store\n" \
                  "(Reset Cursor transform = Slot default)"

    info_view = "Store & Recall Viewport Placement (persp/ortho, loc, rot)\n" \
                "Clear Slot: Use & Set a stored view to the same slot\n" \
                "(without moving the viewport camera)"

    def draw(self, context):
        kt = context.scene.kekit_temp

        layout = self.layout
        # CURSOR BOOKMARKS
        row = layout.row(align=True)
        row.label(text="Cursor Bookmarks")
        row.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_cursor

        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"

        if sum(kt.cursorslot1) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="1", depress=True).mode = "USE1"
        if sum(kt.cursorslot2) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="2", depress=True).mode = "USE2"
        if sum(kt.cursorslot3) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="3", depress=True).mode = "USE3"
        if sum(kt.cursorslot4) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="4", depress=True).mode = "USE4"
        if sum(kt.cursorslot5) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="5", depress=True).mode = "USE5"
        if sum(kt.cursorslot6) == 0:
            row.operator('view3d.ke_cursor_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('view3d.ke_cursor_bookmark', text="6", depress=True).mode = "USE6"

        # VIEW BOOKMARKS
        row = layout.row(align=True)
        row.label(text="View Bookmarks")
        row.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_view

        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('view3d.ke_view_bookmark', text="", icon="IMPORT").mode = "SET6"
        if sum(kt.viewslot1) == 0:
            row.operator('view3d.ke_view_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('view3d.ke_view_bookmark', text="1", depress=True).mode = "USE1"
        if sum(kt.viewslot2) == 0:
            row.operator('view3d.ke_view_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('view3d.ke_view_bookmark', text="2", depress=True).mode = "USE2"
        if sum(kt.viewslot3) == 0:
            row.operator('view3d.ke_view_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('view3d.ke_view_bookmark', text="3", depress=True).mode = "USE3"
        if sum(kt.viewslot4) == 0:
            row.operator('view3d.ke_view_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('view3d.ke_view_bookmark', text="4", depress=True).mode = "USE4"
        if sum(kt.viewslot5) == 0:
            row.operator('view3d.ke_view_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('view3d.ke_view_bookmark', text="5", depress=True).mode = "USE5"
        if sum(kt.viewslot6) == 0:
            row.operator('view3d.ke_view_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('view3d.ke_view_bookmark', text="6", depress=True).mode = "USE6"

        sub = layout.row(align=True)
        sub.alignment = "CENTER"
        sub.operator('view3d.ke_viewpos', text="Get").mode = "GET"
        sub.prop(kt, "view_query", text="")
        sub.operator('view3d.ke_viewpos', text="Set").mode = "SET"

        row = layout.row()
        row.operator('view3d.ke_view_bookmark_cycle', text="Cycle View Bookmarks")


class UISnapComboNames(Panel):
    bl_idname = "UI_PT_ke_snapping_combo_names"
    bl_label = "SnapCombo Names"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_combos = "Snapping Combos: Store & Restore snapping settings\n" \
                  "Define Snapping Combos in the regular Blender SNAPPING MENU.\n" \
                  "Rename slots here (& set AutoSnap option)"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_combos

    def draw(self, context):
        layout = self.layout
        k = get_prefs()
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id
        f = 0.06
        col = layout.column(align=True)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="1")
        split.prop(k, "snap_name1", text="", icon_value=s1)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="2")
        split.prop(k, "snap_name2", text="", icon_value=s2)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="3")
        split.prop(k, "snap_name3", text="", icon_value=s3)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="4")
        split.prop(k, "snap_name4", text="", icon_value=s4)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="5")
        split.prop(k, "snap_name5", text="", icon_value=s5)
        row = col.row(align=True)
        split = row.split(factor=f, align=True)
        split.label(text="6")
        split.prop(k, "snap_name6", text="", icon_value=s6)
        col.prop(k, "combo_autosnap")


class UISnapCombos(Panel):
    bl_idname = "UI_PT_ke_snapping_combos"
    bl_label = "Snapping Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = "VIEW3D_PT_snapping"

    def draw(self, context):
        f = 0.6
        s1 = pcoll['kekit']['ke_snap1'].icon_id
        s2 = pcoll['kekit']['ke_snap2'].icon_id
        s3 = pcoll['kekit']['ke_snap3'].icon_id
        s4 = pcoll['kekit']['ke_snap4'].icon_id
        s5 = pcoll['kekit']['ke_snap5'].icon_id
        s6 = pcoll['kekit']['ke_snap6'].icon_id
        layout = self.layout
        row = layout.row(align=True)
        col = row.column_flow(columns=6, align=True)
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="  1")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET1"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s1).mode = "SET1"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="2")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET2"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s2).mode = "SET2"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="3")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET3"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s3).mode = "SET3"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="4")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET4"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s4).mode = "SET4"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="5")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET5"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s5).mode = "SET5"
        c = col.row(align=True)
        c.alignment = "CENTER"
        c.scale_y = f
        c.label(text="6")
        col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET6"
        col.operator('view3d.ke_snap_combo', text="", icon_value=s6).mode = "SET6"


class UIOpcModule(Panel):
    bl_idname = "UI_PT_M_OPC"
    bl_label = "O&P Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_combos = "Orientation & Pivot Combos:\n" \
                  "Store & Restore O&P combinations for both Object & Edit Mode in hotkeyable slots"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_combos

    def draw(self, context):
        layout = self.layout


class UIopc1(Panel):
    bl_idname = "UI_PT_OPC1"
    bl_label = "OPC 1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc1_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc1_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc1'].icon_id, text="%s" % name).combo = "1"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC1 Object Mode")
        col.prop(k, 'opc1_obj_o')
        col.prop(k, 'opc1_obj_p')
        col.label(text="OPC1 Edit Mode")
        col.prop(k, 'opc1_edit_o')
        col.prop(k, 'opc1_edit_p')


class UIopc2(Panel):
    bl_idname = "UI_PT_OPC2"
    bl_label = "OPC 2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc2_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc2_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc2'].icon_id, text="%s" % name).combo = "2"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC2 Object Mode")
        col.prop(k, 'opc2_obj_o')
        col.prop(k, 'opc2_obj_p')
        col.label(text="OPC2 Edit Mode")
        col.prop(k, 'opc2_edit_o')
        col.prop(k, 'opc2_edit_p')


class UIopc3(Panel):
    bl_idname = "UI_PT_OPC3"
    bl_label = "OPC 3"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc3_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc3_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc3'].icon_id, text="%s" % name).combo = "3"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC3 Object Mode")
        col.prop(k, 'opc3_obj_o')
        col.prop(k, 'opc3_obj_p')
        col.label(text="OPC3 Edit Mode")
        col.prop(k, 'opc3_edit_o')
        col.prop(k, 'opc3_edit_p')


class UIopc4(Panel):
    bl_idname = "UI_PT_OPC4"
    bl_label = "OPC 4"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc4_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc4_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc4'].icon_id, text="%s" % name).combo = "4"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC4 Object Mode")
        col.prop(k, 'opc4_obj_o')
        col.prop(k, 'opc4_obj_p')
        col.label(text="OPC4 Edit Mode")
        col.prop(k, 'opc4_edit_o')
        col.prop(k, 'opc4_edit_p')


class UIopc5(Panel):
    bl_idname = "UI_PT_OPC5"
    bl_label = "OPC 5"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc5_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc5_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc5'].icon_id, text="%s" % name).combo = "5"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC5 Object Mode")
        col.prop(k, 'opc5_obj_o')
        col.prop(k, 'opc5_obj_p')
        col.label(text="OPC5 Edit Mode")
        col.prop(k, 'opc5_edit_o')
        col.prop(k, 'opc5_edit_p')


class UIopc6(Panel):
    bl_idname = "UI_PT_OPC6"
    bl_label = "OPC 6"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        name = k.opc6_name
        toggle = context.scene.kekit_temp.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc6_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=pcoll['kekit']['ke_opc6'].icon_id, text="%s" % name).combo = "6"
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC6 Object Mode")
        col.prop(k, 'opc6_obj_o')
        col.prop(k, 'opc6_obj_p')
        col.label(text="OPC6 Edit Mode")
        col.prop(k, 'opc6_edit_o')
        col.prop(k, 'opc6_edit_p')


classes = (
    UIBookmarksModule,
    KeCursorBookmarks,
    KeViewBookmark,
    KeViewBookmarkCycle,
    KeViewPos,
    KeSnapCombo,
    UISnapCombos,
    UISnapComboNames,
    UIOpcModule,
    UIopc1,
    UIopc2,
    UIopc3,
    UIopc4,
    UIopc5,
    UIopc6,
    KeOPC,
)


def register():
    prefs = get_prefs()
    if prefs.m_bookmarks:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():

    if "bl_rna" in UIBookmarksModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
