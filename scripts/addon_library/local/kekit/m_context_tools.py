import bpy
from bpy.types import Panel
from ._ui import pcoll
from ._utils import get_prefs
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


class UIContextToolsModule(Panel):
    bl_idname = "UI_PT_M_CONTEXTTOOLS"
    bl_label = "Context Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        u = pcoll['kekit']['ke_uncheck'].icon_id
        c = pcoll['kekit']['ke_check'].icon_id
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator('mesh.ke_contextextrude')
        row.prop(k, "tt_extrude", text="", toggle=True, icon_value=c if k.tt_extrude else u)

        row = col.row(align=True)
        row.operator('mesh.ke_contextbevel')
        row.prop(k, "korean", text="", toggle=True, icon_value=c if k.korean else u)
        row.prop(k, "apply_scale", text="", icon="AUTO", toggle=True)

        row = col.row(align=True)
        row.operator('view3d.ke_contextdelete')
        row.prop(k, "cd_smart", text="", toggle=True, icon_value=c if k.cd_smart else u)
        row.prop(k, "h_delete", text="", icon="CON_CHILDOF", toggle=True)
        row.prop(k, "cd_pluscut", text="", icon="ADD", toggle=True)
        col.operator('mesh.ke_contextdissolve')

        row = col.row(align=True)
        row.operator('view3d.ke_contextselect')
        row.prop(k, "context_select_b", text="", toggle=True, icon_value=c if k.context_select_b else u)
        row.prop(k, "context_select_h", text="", icon="CON_CHILDOF", toggle=True)
        row.prop(k, "context_select_c", text="", icon="COLLECTION_NEW", toggle=True)
        col.operator('view3d.ke_contextselect_extend')
        col.operator('view3d.ke_contextselect_subtract')

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
