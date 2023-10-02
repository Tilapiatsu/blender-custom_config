import bpy
from bpy.types import Panel, Header

from .ke_mouse_axis_move import KeMouseAxisMove
from .ke_tt import KeTT
from .ke_vptransform import KeVPTransform

from .._utils import get_prefs


class UITTModule(Panel):
    bl_idname = "UI_PT_M_TT"
    bl_label = "Transform Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        tt_mode = k.tt_mode
        tt_link = k.tt_linkdupe
        col = layout.column(align=True)
        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="TT Toggle")
        srow.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        srow.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        srow.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        scol.separator(factor=0.6)
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Move").mode = "MOVE"
        srow.operator('view3d.ke_tt', text="TT Rotate").mode = "ROTATE"
        srow.operator('view3d.ke_tt', text="TT Scale").mode = "SCALE"
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Dupe").mode = "DUPE"
        srow.operator('view3d.ke_tt', text="TT Cycle").mode = "TOGGLE_CYCLE"
        scol.separator(factor=0.6)
        srow = scol.row(align=True)
        srow.prop(k, "tt_handles", text="Giz")
        srow.prop(k, "tt_select", text="Sel")
        srow.prop(k, "mam_scl", text="MAS")
        if tt_link:
            scol.operator("view3d.ke_tt", text="Dupe Linked Toggle", icon="LINKED",
                          depress=tt_link).mode = "TOGGLE_DUPE"
        else:
            scol.operator("view3d.ke_tt", text="Dupe Linked Toggle", icon="UNLINKED",
                          depress=tt_link).mode = "TOGGLE_DUPE"
        scol.operator('view3d.ke_tt', text="Force Unlinked", icon="UNLINKED").mode = "F_DUPE"
        scol.operator('view3d.ke_tt', text="Force Linked", icon="LINKED").mode = "F_LINKDUPE"

        col.separator()
        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="Mouse Axis", icon="EMPTY_AXIS")
        srow = scol.row(align=True)
        split = srow.split(factor=0.89, align=True)
        subrow1 = split.row(align=True)
        subrow1.operator('view3d.ke_mouse_axis_move', text="Move").mode = "MOVE"
        subrow1.operator('view3d.ke_mouse_axis_move', text="Rotate").mode = "ROT"
        subrow1.operator('view3d.ke_mouse_axis_move', text="Scale").mode = "SCL"
        subrow2 = split.row(align=True)
        subrow2.prop(k, "mam_scale_mode", text="C", toggle=True)
        srow = scol.row(align=True)
        srow.operator('view3d.ke_mouse_axis_move', text="Move Dupe").mode = "DUPE"
        srow.operator('view3d.ke_mouse_axis_move', text="Move Cursor").mode = "CURSOR"
        col.separator()

        sub = col.box()
        scol = sub.column(align=True)
        scol.label(text="View Plane", icon="AXIS_SIDE")
        scol.operator("VIEW3D_OT_ke_vptransform", text="VPDupe").transform = "COPYGRAB"
        scol.separator(factor=0.6)
        row = scol.row(align=True)
        row.operator("VIEW3D_OT_ke_vptransform", text="VPGrab").transform = "TRANSLATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPRotate").transform = "ROTATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPResize").transform = "RESIZE"
        row = scol.row(align=True)
        row.prop(k, "loc_got", text="GGoT")
        row.prop(k, "rot_got", text="RGoT")
        row.prop(k, "scl_got", text="SGoT")
        scol.prop(k, "vptransform", toggle=True)


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


def set_tt_icon_pos(self, context):
    prefs = get_prefs()
    bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
    bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)
    if prefs.tt_icon_pos == "CENTER":
        bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
    elif prefs.tt_icon_pos == "RIGHT":
        bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)
    elif prefs.tt_icon_pos == "LEFT":
        bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
    # ...else REMOVE only


classes = (
    UITTModule,
    KeMouseAxisMove,
    KeVPTransform,
    KeTT,
    KeTTHeader,
)


def register():
    k = get_prefs()
    if k.m_tt:
        for c in classes:
            bpy.utils.register_class(c)

        if k.tt_icon_pos == "LEFT":
            bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
        elif k.tt_icon_pos == "CENTER":
            bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
        elif k.tt_icon_pos == "RIGHT":
            bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)


def unregister():
    if "bl_rna" in UITTModule.__dict__:
        bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
        bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)

        for c in reversed(classes):
            bpy.utils.unregister_class(c)
