import os

import bpy
import rna_keymap_ui
from bpy.props import StringProperty
from bpy.types import Operator, Header, Panel
from bpy.utils import previews
from ._prefs import get_prefs

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


# NOTE: GENERAL UI ONLY (except TT) (Module UI -> module m_ files)

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
        else:
            # + disabled objmode settings to fill void
            row.enabled = False
            row.separator(factor=1)
            row.label(text="Affect Only")
            row.prop(t, "use_transform_data_origin", text="", icon="PIVOT_INDIVIDUAL", toggle=True)
            row.prop(t, "use_transform_pivot_point_align", text="", icon="ORIENTATION_LOCAL", toggle=True)
            row.prop(t, "use_transform_skip_children", text="", icon="CON_CHILDOF", toggle=True)
            row.separator(factor=14.2)

        layout.separator(factor=f)


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


class KeIconPreload(Header):
    bl_idname = "VIEW3D_HT_KE_ICONPRELOAD"
    bl_region_type = 'HEADER'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        # Terrible OpenGL style preloading to avoid seeing (the most used) icons load
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
    row.operator("kekit.filebrowser", icon="IMPORT")
    row.operator("kekit.prefs_export", icon="EXPORT")
    row.operator("kekit.prefs_reset", icon="LOOP_BACK")
    row = layout.row(align=True)
    split = row.split(factor=0.51, align=True)
    subsplit = split.split(factor=0.25, align=True)
    subsplit.label(text="Tab:")
    subsplit.prop(self, "category", text="")
    split.operator("script.reload", text="Reload Add-ons To Update", icon="FILE_REFRESH")

    # Modules box
    col = layout.column()
    col.emboss = "PULLDOWN_MENU"
    col.prop(self, "show_modules", icon='DISCLOSURE_TRI_DOWN' if self.show_modules else 'DISCLOSURE_TRI_RIGHT')
    if self.show_modules:
        # double box for better(SOME) padding
        box = col.box().box()
        box.emboss = "NORMAL"
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
    col = layout.column()
    col.emboss = "PULLDOWN_MENU"
    col.prop(self, "show_ui", icon='DISCLOSURE_TRI_DOWN' if self.show_ui else 'DISCLOSURE_TRI_RIGHT')
    if self.show_ui:
        box = col.box().box()
        box.emboss = "NORMAL"
        row = box.row()
        row.label(text="keKit UI:")
        row = box.row()
        split = row.split(factor=0.2)
        split.label(text="Tool Settings:")
        row2 = split.row(align=True)
        row2.prop(self, "ext_tools", toggle=True)
        row2.prop(self, "ext_factor")

        if k.m_tt:
            row = box.row()
            split = row.split(factor=0.2)
            row1 = split.row()
            row1.label(text="TT Icons:")
            row = split.row(align=True)
            row.prop(self, "tt_icon_pos", expand=True)

        row = box.grid_flow(columns=4)
        row.prop(self, "color_icons", toggle=True)
        row.prop(self, "kcm", toggle=True)
        row.prop(self, "outliner_extras", toggle=True)
        row.prop(self, "material_extras", toggle=True)
        row.prop(self, "experimental", toggle=True)

        box.label(text="Modal Text:")
        gf = box.grid_flow(row_major=True, columns=2)
        gf.use_property_split = True
        gf.prop(self, "ui_scale")
        gf.prop(self, 'modal_color_header')
        gf.prop(self, 'modal_color_text')
        gf.prop(self, 'modal_color_subtext')

    col = layout.column()
    col.emboss = "PULLDOWN_MENU"
    col.prop(self, "show_shortcuts", icon='DISCLOSURE_TRI_DOWN' if self.show_shortcuts else 'DISCLOSURE_TRI_RIGHT')

    if self.show_shortcuts:
        shortcuts_box = col.row().box()

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        kk_entries = []
        conflicts = {}

        # See, the "ke" naming scheme isn't an ego thing! ;P
        # Real reason: Avoid maintaining a list of ops!
        for km in kc.keymaps:
            entry = []
            for i in km.keymap_items:
                if ".ke_" in i.idname or i.idname.startswith("ke."):
                    entry.append(i)
                    if self.show_conflicts:
                        found = find_conflict(km, i)
                        if found:
                            for cat in found:
                                existing = conflicts.get(cat[0], None)
                                if existing is None:
                                    conflicts[cat[0]] = cat[1]
                                else:
                                    new = list(set(existing + cat[1]))
                                    conflicts[cat[0]] = new
            if entry:
                kk_entries.append((km, entry))

        if kk_entries:
            for km, kmi in kk_entries:
                col = shortcuts_box.column()
                col.label(text=str(km.name))
                for i in kmi:
                    row = col.row()
                    row.context_pointer_set("keymap", km)
                    rna_keymap_ui.draw_kmi([], kc, km, i, row, 0)

        col.separator()
        col.prop(self, "show_conflicts", icon='DISCLOSURE_TRI_DOWN' if self.show_conflicts else 'DISCLOSURE_TRI_RIGHT')

        if self.show_conflicts:
            conflicts_box = col.row().box()
            if conflicts:
                col = conflicts_box.column()
                for k in conflicts.keys():
                    col.label(text=str(k.name))
                    for i in conflicts[k]:
                        row = col.row()
                        col.context_pointer_set("keymap", k)
                        rna_keymap_ui.draw_kmi([], kc, k, i, row, 0)


def find_conflict(skm, i):
    ku = bpy.context.window_manager.keyconfigs.user
    usual_suspects = ['Screen', '3D View', '3D View Generic', 'Object Mode', 'Mesh', 'Curve', 'Armature']
    conflicts = []
    for km in ku.keymaps:
        entry = []
        if km == skm or km.name in usual_suspects:
            for item in km.keymap_items:
                if item.name != i.name and item.active:
                    if (item.type, item.value, item.ctrl, item.alt, item.shift) == \
                            (i.type, i.value, i.ctrl, i.alt, i.shift):
                        entry.append(item)
            if entry:
                conflicts.append((km, entry))
    return conflicts


classes = (
    UIKeKitMain,
    KeMouseOverInfo,
    KeIconPreload,
)


def register():
    load_icons()
    k = get_prefs()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_editor_menus.append(KeIconPreload.draw)

    if k.ext_tools:
        bpy.types.VIEW3D_HT_tool_header.append(draw_tool_options)
    if k.outliner_extras:
        bpy.types.OUTLINER_HT_header.append(draw_extras)


def unregister():
    try:
        bpy.types.OUTLINER_HT_header.remove(draw_extras)
        bpy.types.VIEW3D_HT_tool_header.remove(draw_tool_options)
    except Exception as e:
        print('keKit Draw Extras Headers Unregister Fail: ', e)
        pass

    bpy.types.VIEW3D_MT_editor_menus.remove(KeIconPreload.draw)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for pr in pcoll.values():
        bpy.utils.previews.remove(pr)
    pcoll.clear()
