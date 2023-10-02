import bpy
from bpy.types import Panel
from .ke_activeslice import KeActiveSlice
from .ke_boolknife import KeBoolKnife
from .ke_direct_loop_cut import KeDirectLoopCut, UIDirectLoopCutModule
from .ke_facematch import KeFaceMatch
from .ke_fit2grid import KeFit2Grid
from .ke_ground import KeGround
from .ke_merge_near_selected import KeMergeNearSelected
from .ke_merge_to_active import KeMergeToActive
from .ke_merge_to_mouse import KeMergeToMouse
from .ke_multicut import KeMultiCut, KeMultiCutPrefs, UIMultiCutModule
from .ke_niceproject import KeNiceProject
from .ke_primitive_box_add import KePrimitiveBoxAdd
from .ke_quads import KeQuads
from .ke_quickscale import KeQuickScale
from .ke_unbevel import KeUnbevel
from .ke_zeroscale import KeZeroScale
from .._ui import pcoll
from .._utils import get_prefs


class UIModelingModule(Panel):
    bl_idname = "UI_PT_M_MODELING"
    bl_label = "Modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('mesh.ke_unbevel')
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        if k.unbevel_autoring:
            row2.prop(k, "unbevel_autoring", text="", toggle=True, icon="CHECKMARK")
        else:
            row2.prop(k, "unbevel_autoring", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)
        col.operator('view3d.ke_ground', text="Ground or Center")
        row = col.row(align=True)
        row.operator('view3d.ke_nice_project')
        row.operator('view3d.ke_boolknife')
        col.operator('mesh.ke_activeslice')
        col.operator('mesh.ke_quads')

        col.label(text="Merge To:")
        row = col.row(align=True)
        row.operator('mesh.merge_to_mouse', text="Mouse", icon="MOUSE_MOVE")
        row.operator('mesh.ke_merge_to_active', text="Active")
        row.operator('mesh.ke_merge_near_selected', text="Sel.Range")

        col.label(text="Dimensional")
        col.operator('view3d.ke_fit2grid')
        col.operator('mesh.ke_zeroscale', text="ZeroScale to Cursor").orient_type = "CURSOR"
        col.operator('mesh.ke_facematch')
        row = col.row(align=True)
        row.scale_x = 0.85
        row.prop(k, "qs_user_value", text="QScale")
        row.scale_x = 0.15
        row.prop(k, "qs_unit_size", text="U", toggle=True)
        qsx = row.operator('view3d.ke_quickscale', text="X")
        qsy = row.operator('view3d.ke_quickscale', text="Y")
        qsz = row.operator('view3d.ke_quickscale', text="Z")
        qsx.user_axis = "0"
        qsy.user_axis = "1"
        qsz.user_axis = "2"
        qsx.unit_size = k.qs_unit_size
        qsy.unit_size = k.qs_unit_size
        qsz.unit_size = k.qs_unit_size
        qsx.user_value = k.qs_user_value
        qsy.user_value = k.qs_user_value
        qsz.user_value = k.qs_user_value


classes = (
    UIModelingModule,
    UIMultiCutModule,
    UIDirectLoopCutModule,
    KePrimitiveBoxAdd,
    KeFaceMatch,
    KeQuads,
    KeBoolKnife,
    KeMergeToMouse,
    KeMergeToActive,
    KeMergeNearSelected,
    KeGround,
    KeUnbevel,
    KeZeroScale,
    KeQuickScale,
    KeFit2Grid,
    KeNiceProject,
    KeDirectLoopCut,
    KeMultiCut,
    KeMultiCutPrefs,
    KeActiveSlice,
)


def register():
    k = get_prefs()
    if k.m_modeling:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIModelingModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
