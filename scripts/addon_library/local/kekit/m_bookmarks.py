import bpy
from bpy.types import Panel

from ._ui import pcoll
from ._utils import get_prefs
from .ops.ke_cursor_bookmark import KeCursorBookmarks
from .ops.ke_modifier_preset import KeOMP, UIOMPModule
from .ops.ke_opc import KeOPC
from .ops.ke_snapcombo import KeSnapCombo
from .ops.ke_view_bookmark import KeViewBookmark, KeViewBookmarkCycle, UIViewBookmarksModule, KeViewPos


class UIBookmarksModule(Panel):
    bl_idname = "UI_PT_M_BOOKMARKS"
    bl_label = "Bookmarks & Presets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class UICursorBookmarks(Panel):
    bl_idname = "UI_PT_ke_cursor_bookmarks"
    bl_label = "Cursor Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_cursor = "Store & Recall Cursor Transforms (loc & rot)\n" \
                  "Clear Slot: Reset cursor (zero loc & rot) and store\n" \
                  "(Reset Cursor transform = Slot default)"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_cursor

    def draw(self, context):
        layout = self.layout
        kt = context.scene.kekit_temp

        col = layout.column_flow(columns=6, align=True)  # button menu
        for i in range(1, 7):
            nr = str(i)
            # button menu:
            c = col.row(align=True)
            c.alignment = "CENTER"
            c.scale_y = 0.6
            iv = pcoll['kekit']['ke_cursor' + nr].icon_id
            # I don't know why I switched naming of GET/SET between ops, but here we are...
            col.operator('view3d.ke_cursor_bookmark', icon="IMPORT", text="").mode = "SET" + nr
            stored = getattr(kt, "cursorslot" + nr)
            if sum(stored) < 0.001:
                col.operator('view3d.ke_cursor_bookmark',
                             text="", icon_value=iv, depress=False).mode = "USE" + nr
            else:
                col.operator('view3d.ke_cursor_bookmark',
                             text="", icon_value=iv, depress=True).mode = "USE" + nr


class UISnapComboNames(Panel):
    bl_idname = "UI_PT_ke_snapping_combo_names"
    bl_label = "Snapping Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'UI_PT_M_BOOKMARKS'
    bl_options = {'DEFAULT_CLOSED'}

    info_combos = "Snapping Combos: Store & Restore snapping settings\n" \
                  "Rec: If enabled in prefs, Define Combos in the regular Blender SNAPPING MENU\n" \
                  "Rename slots here (for pie menu)  & set Auto-activate Snap option"

    def draw_header_preset(self, context):
        layout = self.layout
        layout.operator('ke_mouseover.info', text="", icon="QUESTION", emboss=False).text = self.info_combos

    def draw(self, context):
        layout = self.layout
        k = get_prefs()
        col = layout.column(align=True)
        for i in range(1, 7):
            nr = str(i)
            row = col.row(align=True)
            iv = pcoll['kekit']['ke_snap' + nr].icon_id
            row.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET" + nr
            row.prop(k, "snap_name" + nr, text="", icon_value=iv)
            row.operator('view3d.ke_snap_combo', text="", icon_value=iv).mode = "SET" + nr
            col.separator()

        layout.prop(k, "combo_autosnap")


class UISnapCombos(Panel):
    bl_idname = "UI_PT_ke_snapping_combos"
    bl_label = "Snapping Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = "VIEW3D_PT_snapping"

    @classmethod
    def poll(cls, context):
        k = get_prefs()
        return not k.snapcombos_npanel_only

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        col = row.column_flow(columns=6, align=True)
        for i in range(1, 7):
            nr = str(i)
            c = col.row(align=True)
            c.alignment = "CENTER"
            c.scale_y = 0.6
            iv = pcoll['kekit']['ke_snap' + nr].icon_id
            col.operator('view3d.ke_snap_combo', icon="IMPORT", text="").mode = "GET" + nr
            col.operator('view3d.ke_snap_combo', text="", icon_value=iv).mode = "SET" + nr


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
        c1 = pcoll['kekit']['ke_opc1'].icon_id

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc1_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c1, text="%s" % name).combo = "1"
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
        c2 = pcoll['kekit']['ke_opc2'].icon_id

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc2_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c2, text="%s" % name).combo = "2"
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
        c3 = pcoll['kekit']['ke_opc3'].icon_id

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc3_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c3, text="%s" % name).combo = "3"
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
        c4 = pcoll['kekit']['ke_opc4'].icon_id

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc4_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c4, text="%s" % name).combo = "4"
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
        c5 = pcoll['kekit']['ke_opc5'].icon_id

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc5_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c5, text="%s" % name).combo = "5"
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
        c6 = pcoll['kekit']['ke_opc6'].icon_id


        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(k, "opc6_name", text="")
            row.alignment = "CENTER"
            row.prop(context.scene.kekit_temp, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon_value=c6, text="%s" % name).combo = "6"
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
    UICursorBookmarks,
    KeViewBookmark,
    KeViewBookmarkCycle,
    UIViewBookmarksModule,
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
    KeOMP,
    UIOMPModule
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
