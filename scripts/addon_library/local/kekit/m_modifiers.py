import bpy
from bpy.types import Panel
from .ops.ke_shading_toggle import KeShadingToggle
from .ops.ke_weight_toggle import KeWeightToggle
from .ops.ke_showcuttermod import KeShowCutterMod
from .ops.ke_solo_cutter import KeSoloCutter
from .ops.ke_mod_em_vis import KeModEmVis
from .ops.subd_tools import KeSubd, KeSubDStep, UISubDModule
from ._utils import get_prefs


class UIModifiersModule(Panel):
    bl_idname = "UI_PT_M_MODIFIERS"
    bl_label = "Modifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator('view3d.ke_solo_cutter').mode = "ALL"
        row.operator('view3d.ke_solo_cutter', text="Solo PreC").mode = "PRE"
        col.operator('object.ke_showcuttermod')
        col.operator('object.ke_mod_em_vis')

        row = col.row(align=True)
        row.operator('view3d.ke_shading_toggle', text="Flat/Smooth Toggle")
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "shading_tris", text="T", toggle=True)

        row = col.row(align=True)
        row.operator('mesh.ke_toggle_weight', text="Toggle Bevel Weight").wtype = "BEVEL"
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "toggle_same", text="A", toggle=True)

        row = col.row(align=True)
        row.operator('mesh.ke_toggle_weight', text="Toggle Crease Weight").wtype = "CREASE"
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "toggle_same", text="A", toggle=True)


classes = (
    UIModifiersModule,
    UISubDModule,
    KeSubd,
    KeSubDStep,
    KeSoloCutter,
    KeShowCutterMod,
    KeShadingToggle,
    KeWeightToggle,
    KeModEmVis,
)


def register():
    k = get_prefs()
    if k.m_modeling:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIModifiersModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
