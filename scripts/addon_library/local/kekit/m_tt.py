import bpy
from bpy.types import Panel
from .ops.ke_mouse_axis_move import KeMouseAxisMove
from .ops.ke_tt import KeTT
from .ops.ke_vptransform import KeVPTransform
from ._utils import get_prefs


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
        col = layout.column(align=False)
        row = col.row(align=True)
        row.label(text="TT Toggle")
        row = col.row(align=True)
        row.operator('view3d.ke_tt', text="TT Mode Cycle").mode = "TOGGLE_CYCLE"
        row.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        row.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        row.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        col = col.column(align=True)
        row = col.row(align=True)
        row.operator('view3d.ke_tt', text="TT Move").mode = "MOVE"
        row.operator('view3d.ke_tt', text="TT Rotate").mode = "ROTATE"
        row.operator('view3d.ke_tt', text="TT Scale").mode = "SCALE"
        split = col.row(align=True)
        split.operator('view3d.ke_tt', text="TT Dupe (Toggle)").mode = "DUPE"
        split.operator("view3d.ke_tt", text="", icon="LINKED" if tt_link else "UNLINKED",
                       depress=tt_link).mode = "TOGGLE_DUPE"
        # if tt_link:
        #     split.operator("view3d.ke_tt", text="", icon="LINKED",
        #                   depress=tt_link).mode = "TOGGLE_DUPE"
        # else:
        #     split.operator("view3d.ke_tt", text="", icon="UNLINKED",
        #                   depress=tt_link).mode = "TOGGLE_DUPE"
        row = col.row(align=True)
        row.operator('view3d.ke_tt', text="TT Dupe", icon="UNLINKED").mode = "F_DUPE"
        row.operator('view3d.ke_tt', text="Linked", icon="LINKED").mode = "F_LINKDUPE"
        row = col.row(align=True)
        row.prop(k, "tt_handles", text="Giz")
        row.prop(k, "tt_select", text="Sel")
        row.prop(k, "mam_scl", text="MAS")

        col.separator(factor=1.5)
        row = col.row(align=True)
        row.label(text="Mouse Axis", icon="EMPTY_AXIS")
        row = col.row(align=True)
        row.operator('view3d.ke_mouse_axis_move', text="Move").mode = "MOVE"
        row.operator('view3d.ke_mouse_axis_move', text="Rotate").mode = "ROT"
        row.operator('view3d.ke_mouse_axis_move', text="Scale").mode = "SCL"
        row.prop(k, "mam_scale_mode", text="", icon="CON_SIZELIKE", toggle=True)
        row = col.row(align=True)
        row.operator('view3d.ke_mouse_axis_move', text="Move Dupe").mode = "DUPE"

        col.separator(factor=1.5)
        col.label(text="View Plane", icon="AXIS_SIDE")
        row = col.row(align=True)
        row.operator("VIEW3D_OT_ke_vptransform", text="VPGrab").transform = "TRANSLATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPRotate").transform = "ROTATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPResize").transform = "RESIZE"
        col.operator("VIEW3D_OT_ke_vptransform", text="VPDupe").transform = "COPYGRAB"
        row = col.row(align=True)
        row.prop(k, "loc_got", text="GGoT")
        row.prop(k, "rot_got", text="RGoT")
        row.prop(k, "scl_got", text="SGoT")
        col.prop(k, "vptransform", toggle=True)


# class KeTTHeader(Header):
#     bl_idname = "VIEW3D_HT_KE_TT"
#     bl_label = "Transform Toggle Menu"
#     bl_region_type = 'HEADER'
#     bl_space_type = 'VIEW_3D'
#
#     def draw(self, context):
#         k = get_prefs()
#         layout = self.layout
#         tt_mode = k.tt_mode
#         tt_link = k.tt_linkdupe
#         row = layout.row(align=True)
#         row.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
#         row.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
#         row.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
#         row.separator(factor=0.5)
#         if tt_link:
#             row.operator("view3d.ke_tt", text="", icon='LINKED', depress=tt_link).mode = "TOGGLE_DUPE"
#         else:
#             row.operator("view3d.ke_tt", text="", icon='UNLINKED', depress=tt_link).mode = "TOGGLE_DUPE"
#         row.separator(factor=1)
#
#
# def set_tt_icon_pos(self, context):
#     prefs = get_prefs()
#     bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
#     bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)
#     if prefs.tt_icon_pos == "CENTER":
#         bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
#     elif prefs.tt_icon_pos == "RIGHT":
#         bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)
#     elif prefs.tt_icon_pos == "LEFT":
#         bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
#     # ...else REMOVE only


classes = (
    KeMouseAxisMove,
    KeTT,
    KeVPTransform,
    UITTModule,
)


def register():
    k = get_prefs()
    if k.m_tt:
        for c in classes:
            bpy.utils.register_class(c)

        # if k.tt_icon_pos == "LEFT":
        #     bpy.types.VIEW3D_HT_header.prepend(KeTTHeader.draw)
        # elif k.tt_icon_pos == "CENTER":
        #     bpy.types.VIEW3D_MT_editor_menus.append(KeTTHeader.draw)
        # elif k.tt_icon_pos == "RIGHT":
        #     bpy.types.VIEW3D_HT_header.append(KeTTHeader.draw)


def unregister():
    # if "bl_rna" in UITTModule.__dict__:
    # bpy.types.VIEW3D_HT_header.remove(KeTTHeader.draw)
    # bpy.types.VIEW3D_MT_editor_menus.remove(KeTTHeader.draw)

    for c in reversed(classes):
        bpy.utils.unregister_class(c)
