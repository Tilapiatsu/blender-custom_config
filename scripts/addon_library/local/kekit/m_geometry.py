import bpy
from bpy.types import Panel
from .ops.ke_collision import KeCollision
from .ops.ke_copyplus import KeCopyPlus
from .ops.ke_exex import KeExEx
from .ops.ke_extract_and_edit import KeExtractAndEdit
from .ops.ke_fitprim import KeFitPrim, UIFitPrimModule
from .ops.ke_get_set_editmesh import KeGetSetEditMesh
from .ops.ke_linear_array import KeLinearArray
from .ops.ke_local_by_distance import KeLocalByDistance
from .ops.ke_mouse_mirror_flip import KeMouseMirrorFlip
from .ops.ke_polybrush import KePolyBrush
from .ops.ke_quickmeasure import KeQuickMeasure
from .ops.ke_radial_array import KeRadialArray
from .ops.ke_radial_instances import KeRadialInstances
from .ops.ke_unhide_or_local import KeUnhideOrLocal
from .ops.ke_unrotator import KeUnrotator, UIUnrotatorModule
from .ops.ke_vp_flip import KeVPFlip
from .ops.ke_zerolocal import KeZeroLocal
from ._ui import pcoll
from ._utils import get_prefs


class UIGeoModule(Panel):
    bl_idname = "UI_PT_M_GEO"
    bl_label = "Geometry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"

    def draw(self, context):
        k = get_prefs()
        u = pcoll['kekit']['ke_uncheck'].icon_id
        s = 0.78
        m = 0.65

        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        split = row.split(factor=s, align=True)
        subrow1 = split.row(align=True)
        subrow1.operator('view3d.ke_copyplus', text="Cut+").mode = "CUT"
        subrow1.operator('view3d.ke_copyplus', text="Copy+").mode = "COPY"
        subrow1.operator('view3d.ke_copyplus', text="Paste+").mode = "PASTE"
        subrow2 = split.row(align=True)
        subrow2.prop(k, "plus_merge", toggle=True)
        subrow2.prop(k, "plus_mpoint", toggle=True)

        row = col.row(align=True)
        split = row.split(factor=m, align=True)
        split.operator('mesh.ke_extract_and_edit', text="Extract & Edit")
        split.operator('mesh.ke_exex', text="ExEx")

        row = col.row(align=True)
        split = row.split(factor=m, align=True)
        split.operator('view3d.ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="Mouse Mirror").mode = "MIRROR"
        split.operator('view3d.ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="Flip").mode = "FLIP"
        col.operator('view3d.ke_vp_flip')

        row = col.row(align=True)
        split = row.split(factor=s, align=True)
        split.operator("view3d.ke_lineararray", text="Linear Instances").convert = True
        split.operator("view3d.ke_lineararray", text="LA").convert = False

        row = col.row(align=True)
        split = row.split(factor=s, align=True)
        split.operator("view3d.ke_radial_instances")
        split.operator("view3d.ke_radialarray", text="RA")

        row = col.row(align=True)
        row.operator('view3d.ke_collision', text="BBox").col_type = "BOX"
        row.operator('view3d.ke_collision', text="Convex Hull").col_type = "CONVEX"
        col.operator('object.ke_polybrush')

        col.separator(factor=0.5)

        row = col.row(align=True)
        split = row.split(factor=s, align=True)
        split.operator('view3d.ke_quickmeasure', icon="DRIVER_DISTANCE", text="QuickMeasure").qm_start = "DEFAULT"
        split.operator('view3d.ke_quickmeasure', text="QMF").qm_start = "SEL_SAVE"

        row = col.row(align=True)
        split = row.split(factor=s, align=True)
        split.operator('view3d.ke_get_set_editmesh', icon="MOUSE_MOVE", text="Get&Set EditMode")
        row2 = split.row(align=True)
        split2 = row2.split(factor=0.5, align=True)  # coz checkmark & single letter != same size
        split2.operator('view3d.ke_get_set_editmesh', text="E").extend = True
        if k.getset_ep:
            split2.prop(k, "getset_ep", text="", toggle=True, icon="CHECKMARK")
        else:
            split2.prop(k, "getset_ep", text="", toggle=True, icon_value=u)

        row = col.row(align=True)
        split = row.split(factor=0.5, align=True)  # coz weird flicker w. only align here
        split.operator('view3d.ke_zerolocal', icon="HIDE_OFF")
        split.operator('object.ke_local_by_distance', text="Local By Dist.")

        col.operator('view3d.ke_unhide_or_local', icon="HIDE_OFF")


classes = (
    KeCollision,
    KeCopyPlus,
    KeExEx,
    KeExtractAndEdit,
    KeFitPrim,
    KeGetSetEditMesh,
    KeLinearArray,
    KeLocalByDistance,
    KeMouseMirrorFlip,
    KePolyBrush,
    KeQuickMeasure,
    KeRadialArray,
    KeRadialInstances,
    KeUnhideOrLocal,
    KeUnrotator,
    KeVPFlip,
    KeZeroLocal,
    UIGeoModule,
    UIFitPrimModule,
    UIUnrotatorModule,
)


def register():
    if get_prefs().m_geo:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIGeoModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
