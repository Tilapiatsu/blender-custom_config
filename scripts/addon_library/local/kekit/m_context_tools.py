import bpy
from bpy.types import Panel
from .ops.context_operators import (
    KeContextDissolve,
    KeContextSelect,
    KeContextSelectExtend,
    KeContextSelectSubtract,
    KeContextExtrude,
    KeContextDelete,
    KeContextBevel,
    KeContextSlide
)
from .ops.ke_bridge_or_fill import KeBridgeOrFill
from .ops.ke_context_connect import KeContextConnect
from .ops.ke_triple_connect_spin import KeTripleConnectSpin
from ._utils import get_prefs


class UIContextToolsModule(Panel):
    bl_idname = "UI_PT_M_CONTEXTTOOLS"
    bl_label = "Context Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=False)
        split = row.split(factor=.7, align=True)
        split.operator('mesh.ke_contextbevel')
        split2 = split.row(align=True)
        split2.prop(k, "apply_scale", toggle=True)
        split2.prop(k, "korean", text="K/F", toggle=True)

        row = col.row(align=False)
        split = row.split(factor=.7, align=True)
        split.operator('mesh.ke_contextextrude')
        split2 = split.row(align=True)
        split2.prop(k, "tt_extrude", text="TT", toggle=True)

        row = col.row(align=False)
        split = row.split(factor=.6, align=True)
        split.operator('view3d.ke_contextdelete')
        split2 = split.row(align=True)
        split2.prop(k, "cd_smart", text="S", toggle=True)
        split2.prop(k, "h_delete", text="H", toggle=True)
        split2.prop(k, "cd_pluscut", text="+", toggle=True)
        col.operator('mesh.ke_contextdissolve')

        col.separator(factor=0.5)
        row = col.row(align=False)
        split = row.split(factor=.5, align=True)
        split.label(text=" C.Select:")
        split2 = split.row(align=True)
        split2.prop(k, "context_select_h", toggle=True)
        split2.prop(k, "context_select_b", toggle=True)
        split2.prop(k, "context_select_c", toggle=True)

        col.operator('view3d.ke_contextselect')
        col.operator('view3d.ke_contextselect_extend')
        col.operator('view3d.ke_contextselect_subtract')

        col.separator(factor=0.5)
        col.operator('mesh.ke_bridge_or_fill')
        col.operator('mesh.ke_context_connect')
        col.operator('mesh.ke_triple_connect_spin')

        col.operator('mesh.ke_contextslide')


classes = (
    KeBridgeOrFill,
    KeContextBevel,
    KeContextConnect,
    KeContextDelete,
    KeContextDissolve,
    KeContextExtrude,
    KeContextSelect,
    KeContextSelectExtend,
    KeContextSelectSubtract,
    KeContextSlide,
    KeTripleConnectSpin,
    UIContextToolsModule,
)


def register():
    if get_prefs().m_contexttools:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIContextToolsModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
