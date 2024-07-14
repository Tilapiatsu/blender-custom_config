import os

import bpy
import rna_keymap_ui
from bpy.props import StringProperty
from bpy.types import Operator, Header, Panel
from bpy.utils import previews
from ._prefs import get_prefs
from ._utils import get_kekit_keymap

pcoll = {}
icons = ["ke_bm1.png", "ke_bm2.png", "ke_bm3.png", "ke_bm4.png", "ke_bm5.png", "ke_bm6.png", "ke_check.png",
         "ke_cursor1.png", "ke_cursor2.png", "ke_cursor3.png", "ke_cursor4.png", "ke_cursor5.png", "ke_cursor6.png",
         "ke_dot1.png", "ke_dot2.png", "ke_dot3.png", "ke_dot4.png", "ke_dot5.png", "ke_dot6.png",
         "ke_mono1.png", "ke_mono2.png", "ke_mono3.png", "ke_mono4.png", "ke_mono5.png", "ke_mono6.png",
         "ke_opc1.png", "ke_opc2.png", "ke_opc3.png", "ke_opc4.png", "ke_opc5.png", "ke_opc6.png",
         "ke_snap1.png", "ke_snap2.png", "ke_snap3.png", "ke_snap4.png", "ke_snap5.png", "ke_snap6.png",
         "ke_uncheck.png"]

kekit_version = (0, 0, 0)  # is set from __init__
kit_cat = ""  # is set from __init__
shortcuts_session_temp = {}


#
# MAIN KIT UI
#
class UIKeKitMain(Panel):
    bl_idname = "UI_PT_kekit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_label = 'keKit'
    bl_description = 'keKit Main Panel'

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
        row = layout.row(align=False)
        row.label(text="%s %s" % (kekit_version, kit_cat))
        row.operator("wm.url_open", text="", icon="URL").url = "https://ke-code.xyz/scripts/kekit.html"

    def draw(self, context):
        layout = self.layout


def prefs_ui(self, layout):
    k = get_prefs()
    box = layout.box()
    row = box.row()
    row.operator("kekit.prefs_export", icon="EXPORT")
    row.operator("kekit.prefs_import", icon="IMPORT")
    row.operator("kekit.prefs_reset", icon="LOOP_BACK")
    row = layout.row(align=True)
    split = row.split(factor=0.51, align=True)
    subsplit = split.split(factor=0.25, align=True)
    subsplit.label(text="Tab:")
    subsplit.prop(self, "category", text="")
    split.operator("script.reload", text="Reload Add-ons To Update", icon="FILE_REFRESH")

    # Modules box
    box = layout.box()
    col = box.column()
    col.emboss = "PULLDOWN_MENU"
    # Todo: Replace with 4.1 "layout panels" (for submenus) ...at some point post 4.1 release
    # header, panel = layout.panel("my_panel_id", default_closed=False)
    #         header.label(text="Hello World")
    col.prop(self, "show_modules", icon='DISCLOSURE_TRI_DOWN' if self.show_modules else 'DISCLOSURE_TRI_RIGHT')
    if self.show_modules:
        # double box for better(SOME) padding
        box = col.box().box()
        box.emboss = "NORMAL"
        row = box.row()
        row.alignment = "CENTER"
        row.enabled = False
        row.label(text="Reload Add-ons or restart Blender to apply Module choices:")
        gf = box.grid_flow(row_major=True, columns=3)
        gf.prop(self, "m_geo", toggle=True)
        gf.prop(self, "m_render", toggle=True)
        gf.prop(self, "m_bookmarks", toggle=True)
        gf.prop(self, "m_selection", toggle=True)
        gf.prop(self, "m_modeling", toggle=True)
        gf.prop(self, "m_modifiers", toggle=True)
        gf.prop(self, "m_contexttools", toggle=True)
        gf.prop(self, "m_tt", toggle=True)
        gf.prop(self, "m_cleanup", toggle=True)
        gf.prop(self, "m_piemenus", toggle=True)

    # UI Box
    box = layout.box()
    col = box.column()
    col.emboss = "PULLDOWN_MENU"
    col.prop(self, "show_ui", icon='DISCLOSURE_TRI_DOWN' if self.show_ui else 'DISCLOSURE_TRI_RIGHT')
    if self.show_ui:
        box = col.box().box()
        box.emboss = "NORMAL"

        row = box.row()
        row.label(text="keKit UI:")
        row = box.grid_flow(columns=4)
        row.prop(self, "color_icons", toggle=True)
        row.prop(self, "kcm", toggle=True)
        row.prop(self, "outliner_extras", toggle=True)
        row.prop(self, "material_extras", toggle=True)
        row.prop(self, "experimental", toggle=True)
        row.prop(self, "obj_menu", toggle=True)

        if k.m_tt:
            row = box.row()
            split = row.split(factor=0.2)
            row1 = split.row()
            row1.label(text="TT Icons:")
            row = split.row(align=True)
            row.prop(self, "tt_icon_pos", expand=True)

        row = box.row()
        split = row.split(factor=0.2)
        split.label(text="Tool Settings:")
        row2 = split.row(align=True)
        row2.prop(self, "ext_tools", toggle=True)
        row2.prop(self, "ext_factor")

        box.label(text="Modal Text:")
        gf = box.grid_flow(row_major=True, columns=2)
        gf.use_property_split = True
        gf.prop(self, "ui_scale")
        gf.prop(self, 'modal_color_header')
        gf.prop(self, 'modal_color_text')
        gf.prop(self, 'modal_color_subtext')

    # Shortcut Boxes
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    count = 0
    global shortcuts_session_temp

    # SHORTCUT / KEYMAP TOOLS
    box = layout.box()
    col = box.column()
    col.emboss = "PULLDOWN_MENU"
    col.prop(self, "show_kmtools", icon='DISCLOSURE_TRI_DOWN' if self.show_kmtools else 'DISCLOSURE_TRI_RIGHT')

    if self.show_kmtools:
        main_col = box.column()
        main_col.alignment = "CENTER"
        top_col = main_col.column()
        row = top_col.row()
        row.prop(self, 'km_mode', expand=True)
        col = main_col.column()

        if self.km_mode == "ASSIGNED":
            kk_entries = get_kekit_keymap()

            if kk_entries:
                for km, kmi in kk_entries:
                    row = col.row()
                    row.label(text=km.name)
                    for i in kmi:
                        count += 1
                        row = col.row()
                        row.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, i, row, 0)

            row = top_col.row()
            row.alignment = "CENTER"
            row.label(text="[ %s Shortcuts ]" % count)

        elif self.km_mode == "CONFLICT":
            # Very slow - To-do: Make not slow (Do I really care?)
            kkm = get_kekit_keymap()
            if kkm:
                row = col.row()
                row.alignment = "CENTER"
                row.enabled = False
                row.label(text="Note: These are only 'possible' conflicts - false positives are likely")

                for km, kmi in kkm:
                    for i in kmi:
                        found = find_conflict(kc, i)
                        if found:
                            box = col.box()
                            row = box.row()
                            row.enabled = False
                            row.label(text=i.idname)
                            for fkm, fkmi in found.items():
                                for fi in fkmi:
                                    count += 1
                                    srow = box.row(align=True)
                                    srow.separator(factor=2)
                                    srow.label(text=fkm.name)
                                    srow = srow.column()
                                    srow.context_pointer_set("keymap", fkm)
                                    rna_keymap_ui.draw_kmi([], kc, fkm, fi, srow, 0)

                row = top_col.row()
                row.alignment = "CENTER"
                row.label(text="[ Found %s Candidates ]" % count)

        elif self.km_mode == "USELESS":
            row = col.row()
            row.alignment = "CENTER"
            row.enabled = False

            for km in kc.keymaps:
                for i in km.keymap_items:
                    if not operator_exists(i.idname):
                        srow = col.row()
                        count += 1
                        col.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, i, srow, 0)
            if count:
                row.label(text="Note: Some shortcuts may need to be removed in Prefs/Keymap")
            row = top_col.row()
            row.alignment = "CENTER"
            row.label(text="[ Found %s Candidates ]" % count)


#
# UI UTILITY OPERATORS
#
def find_conflict(ku, i):
    # ku = bpy.context.window_manager.keyconfigs.user
    usual_suspects = ['Screen', '3D View', '3D View Generic', 'Object Mode', 'Mesh', 'Curve', 'Armature']
    conflicts = {}
    for km in ku.keymaps:
        entry = []
        if km.name in usual_suspects:
            for item in km.keymap_items:
                if item.name != i.name and item.active:
                    if item.type == i.type:
                        if (item.value, item.ctrl, item.alt, item.shift) == (i.value, i.ctrl, i.alt, i.shift):
                            entry.append(item)
        if entry:
            conflicts[km] = entry
    return conflicts


def operator_exists(idname):
    # The only way I found that correctly finds "left over operators"...
    names = idname.split(".")
    a = bpy.ops
    for prop in names:
        a = getattr(a, prop)
    try:
        name = a.__repr__()
    except AttributeError as e:
        # print(e)
        return False
    return True


class KeMouseOverInfo(Operator):
    bl_idname = "ke_mouseover.info"
    bl_label = "Info"
    bl_options = {"INTERNAL"}

    text: StringProperty(name="Info", description="Info", default='')

    @classmethod
    def description(cls, context, properties):
        return properties.text

    def execute(self, context):
        return {'INTERFACE'}


#
# KEKIT EXTRAS UI
#
def load_icons():
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pr = previews.new()
    for i in icons:
        name = i[:-4]
        pr.load(name, os.path.join(icons_dir, i), 'IMAGE')
    pcoll['kekit'] = pr


def draw_extras(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("outliner.show_active", icon="ZOOM_PREVIOUS", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_IN", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_OUT", text="").open = False


def draw_tool_options(self, context):
    k = get_prefs()
    if k.ext_tools:
        f = k.ext_factor
        t = context.tool_settings
        layout = self.layout
        row = layout.row(align=True)

        if context.mode == "OBJECT" and context.object:
            if context.object.type == "MESH":
                row.enabled = False
                row.separator(factor=1)
                row.label(icon='MOD_MIRROR')
                sub = row.row(align=True)
                sub.scale_x = 0.6
                sub.prop(context.object, "use_mesh_mirror_x", text="X", toggle=True)
                sub.prop(context.object, "use_mesh_mirror_y", text="Y", toggle=True)
                sub.prop(context.object, "use_mesh_mirror_z", text="Z", toggle=True)
                row.prop(t, "use_mesh_automerge", text="")
                row.separator(factor=1)
                row.prop(t, "use_transform_correct_face_attributes", text="", icon="MOD_UVPROJECT", toggle=True)
                row.prop(t, "use_edge_path_live_unwrap", text="", icon="UV", toggle=True)
            else:
                row.separator(factor=1.8)
                row.label(text="Affect Only")
                row.prop(t, "use_transform_data_origin", text="", icon="PIVOT_INDIVIDUAL", toggle=True)
                row.prop(t, "use_transform_pivot_point_align", text="", icon="ORIENTATION_LOCAL", toggle=True)
                row.prop(t, "use_transform_skip_children", text="", icon="CON_CHILDOF", toggle=True)
                row.separator(factor=1.8)

        elif context.mode == "EDIT_MESH":
            row.separator(factor=0.6)
            row.prop(t, "use_transform_correct_face_attributes", text="", icon="MOD_UVPROJECT", toggle=True)
            row.prop(t, "use_edge_path_live_unwrap", text="", icon="UV", toggle=True)

        elif context.mode == "EDIT_ARMATURE":
            # + disabled objmode settings to fill void
            row.enabled = False
            row.separator(factor=3)
            row.prop(t, "use_transform_data_origin", text="", icon="PIVOT_INDIVIDUAL", toggle=True)
            row.prop(t, "use_transform_pivot_point_align", text="", icon="ORIENTATION_LOCAL", toggle=True)
            row.prop(t, "use_transform_skip_children", text="", icon="CON_CHILDOF", toggle=True)
            row.separator(factor=3.8)

        elif context.mode == "PAINT_TEXTURE":
            row.separator(factor=11)

        elif context.mode == "PAINT_VERTEX":
            row.separator(factor=19.5)

        elif context.mode == "PAINT_WEIGHT":
            row.separator(factor=7.5)

        else:
            pass
            # meh do nothing
            # + disabled objmode settings to fill void
            # row.enabled = False
            # row.separator(factor=1)
            # row.label(text="Affect Only")
            # row.prop(t, "use_transform_data_origin", text="", icon="PIVOT_INDIVIDUAL", toggle=True)
            # row.prop(t, "use_transform_pivot_point_align", text="", icon="ORIENTATION_LOCAL", toggle=True)
            # row.prop(t, "use_transform_skip_children", text="", icon="CON_CHILDOF", toggle=True)
            # row.separator(factor=14.2)

        layout.separator(factor=f)


class KeCursorMenuHeader(Header):
    bl_idname = "VIEW3D_HT_KCM"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'
    bl_label = "keKit Cursor Menu"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="VIEW3D_PT_KCM", icon="CURSOR", text="")


class KeCursorMenuPanel(Panel):
    bl_idname = "VIEW3D_PT_KCM"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'
    bl_label = "KCM"

    def draw(self, context):
        kt = context.scene.kekit_temp
        k = get_prefs()
        if k.color_icons:
            c1 = pcoll['kekit']['ke_cursor1'].icon_id
            c2 = pcoll['kekit']['ke_cursor2'].icon_id
            c3 = pcoll['kekit']['ke_cursor3'].icon_id
            c4 = pcoll['kekit']['ke_cursor4'].icon_id
            c5 = pcoll['kekit']['ke_cursor5'].icon_id
            c6 = pcoll['kekit']['ke_cursor6'].icon_id
        else:
            c1 = pcoll['kekit']['ke_mono1'].icon_id
            c2 = pcoll['kekit']['ke_mono2'].icon_id
            c3 = pcoll['kekit']['ke_mono3'].icon_id
            c4 = pcoll['kekit']['ke_mono4'].icon_id
            c5 = pcoll['kekit']['ke_mono5'].icon_id
            c6 = pcoll['kekit']['ke_mono6'].icon_id

        xp = k.experimental
        bookmarks = bool(k.m_bookmarks)

        layout = self.layout
        c = layout.column()

        c.operator("view3d.ke_cursor_rotation", text="Align Cursor To View").mode = "VIEW"

        c.label(text="Step Rotate")
        col = c.column(align=True)
        row = col.row(align=True)
        row.prop(kt, "kcm_axis", expand=True)

        row = col.row(align=True)
        row.prop(kt, "kcm_rot_preset", expand=True)

        # flagged as "experimental"  due to "unsupported RNA type 2" error-spam, solution TBD
        row = col.row(align=True)
        if xp:
            row.prop(kt, "kcm_custom_rot")

        row = col.row(align=True)
        row.operator("view3d.ke_cursor_rotation", text="Step Rotate").mode = "STEP"

        if xp:
            c.label(text="Target Object")
            c.prop_search(context.scene, "kekit_cursor_obj", bpy.data, "objects", text="")
        row = c.row(align=True)
        row.operator("view3d.ke_cursor_rotation", text="Point To Obj").mode = "OBJECT"
        row.operator("view3d.ke_cursor_rotation", text="Copy Obj Rot").mode = "MATCH"

        c.label(text="Snap Cursor To")
        col = c.column(align=True)
        row = col.row(align=True)
        row.operator("view3d.snap_cursor_to_selected", text="Sel.")
        row.operator("view3d.snap_cursor_to_active", text="Active")
        row.operator("view3d.snap_cursor_to_grid", text="Grid")
        row.operator("view3d.ke_cursor_ortho_snap", text="Ortho")

        if bookmarks:
            c.label(text="Cursor Bookmarks")
            row = c.grid_flow(row_major=True, columns=6, align=True)
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"
            row.operator('view3d.ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"

            if sum(kt.cursorslot1) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c1, depress=False).mode = "USE1"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c1, depress=True).mode = "USE1"
            if sum(kt.cursorslot2) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c2, depress=False).mode = "USE2"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c2, depress=True).mode = "USE2"
            if sum(kt.cursorslot3) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c3, depress=False).mode = "USE3"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c3, depress=True).mode = "USE3"
            if sum(kt.cursorslot4) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c4, depress=False).mode = "USE4"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c4, depress=True).mode = "USE4"
            if sum(kt.cursorslot5) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c5, depress=False).mode = "USE5"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c5, depress=True).mode = "USE5"
            if sum(kt.cursorslot6) == 0:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c6, depress=False).mode = "USE6"
            else:
                row.operator('view3d.ke_cursor_bookmark', text="", icon_value=c6, depress=True).mode = "USE6"

        if xp:
            # flagged as "experimental" due to "unsupported RNA type 2" error-spam, solution TBD
            cf = c.column_flow(columns=2, align=True)
            cf.prop(context.scene.cursor, "location", text="Cursor Location", expand=True)
            cf.operator("view3d.snap_cursor_to_center", text="Clear Loc")
            cf.prop(context.scene.cursor, "rotation_euler", text="Cursor Rotation", expand=True)
            cf.operator("view3d.ke_cursor_clear_rot", text="Clear Rot")
        else:
            c.separator(factor=1)
            row = c.row(align=True)
            row.operator("view3d.snap_cursor_to_center", text="Clear Loc")
            row.operator("view3d.ke_cursor_clear_rot", text="Clear Rot")

        c.operator("view3d.snap_cursor_to_center", text="Reset Cursor")


class KeTTHeader(Header):
    bl_idname = "VIEW3D_HT_KE_TT"
    bl_label = "Transform Toggle Menu"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        tt_mode = k.tt_mode
        tt_link = k.tt_linkdupe
        row = layout.row(align=True)
        row.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        row.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        row.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        row.separator(factor=0.5)
        if tt_link:
            row.operator("view3d.ke_tt", text="", icon='LINKED', depress=tt_link).mode = "TOGGLE_DUPE"
        else:
            row.operator("view3d.ke_tt", text="", icon='UNLINKED', depress=tt_link).mode = "TOGGLE_DUPE"
        row.separator(factor=1)


def draw_syncvpbutton(self, context):
    layout = self.layout
    row = layout.row()
    row.use_property_split = True
    row.operator("view3d.ke_syncvpmaterial", icon="COLOR").active_only = True


def menu_show_in_outliner(self, context):
    self.layout.operator("view3d.ke_show_in_outliner", text="Show in Outliner")


def menu_set_active_collection(self, context):
    self.layout.operator("view3d.ke_set_active_collection", text="Set Active Collection")


class KeIconPreload(Header):
    bl_idname = "VIEW3D_HT_KE_ICONPRELOAD"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        # Terrible OpenGL style preloading just to avoid seeing (the most used) icons load
        layout = self.layout
        row = layout.row()
        row.ui_units_x = 0.01
        row.scale_y = 0.01
        row.scale_x = 0.01
        # SNAPPING
        row.label(icon_value=pcoll['kekit']['ke_snap1'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap2'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap3'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap4'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap5'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_snap6'].icon_id)
        # OPC
        row.label(icon_value=pcoll['kekit']['ke_opc1'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc2'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc3'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc4'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc5'].icon_id)
        row.label(icon_value=pcoll['kekit']['ke_opc6'].icon_id)


#
# REGISTERING
#
classes = (
    KeCursorMenuHeader,
    KeCursorMenuPanel,
    KeIconPreload,
    KeMouseOverInfo,
    KeTTHeader,
    UIKeKitMain,
)


def add_extras(k):
    if k.ext_tools:
        bpy.types.VIEW3D_HT_tool_header.append(draw_tool_options)
    if k.outliner_extras:
        bpy.types.OUTLINER_HT_header.append(draw_extras)
    if k.m_tt:
        if k.tt_icon_pos == "LEFT":
            bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
        elif k.tt_icon_pos == "CENTER":
            bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
        elif k.tt_icon_pos == "RIGHT":
            bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)
    if k.kcm:
        bpy.types.VIEW3D_MT_editor_menus.append(KeCursorMenuHeader.draw)
    if k.material_extras and k.m_render:
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(draw_syncvpbutton)
    # Object Context Menu Extras (selection module)
    if k.m_selection and k.obj_menu:
        bpy.types.VIEW3D_MT_object_context_menu.append(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.append(menu_show_in_outliner)


def remove_extras():
    try:
        bpy.types.OUTLINER_HT_header.remove(draw_extras)
        bpy.types.VIEW3D_HT_tool_header.remove(draw_tool_options)
        bpy.types.VIEW3D_MT_editor_menus.remove(KeCursorMenuHeader.draw)
        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_set_active_collection)
        bpy.types.VIEW3D_MT_object_context_menu.remove(menu_show_in_outliner)
        bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
        bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(draw_syncvpbutton)
    except Exception as e:
        print('keKit Extras Unregister Fail: ', e)
        pass


def register():
    load_icons()
    k = get_prefs()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_editor_menus.append(KeIconPreload.draw)
    add_extras(k)


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(KeIconPreload.draw)
    remove_extras()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for pr in pcoll.values():
        bpy.utils.previews.remove(pr)

    pcoll.clear()
    shortcuts_session_temp.clear()
