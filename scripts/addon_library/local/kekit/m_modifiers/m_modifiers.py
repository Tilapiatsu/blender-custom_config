import bpy
from bpy.types import Panel

from .ke_shading_toggle import KeShadingToggle
from .ke_showcuttermod import KeShowCutterMod
from .ke_solo_cutter import KeSoloCutter
from .subd_tools import KeSubd, KeSubDStep, UISubDModule

from .._utils import get_prefs


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
        row = col.row(align=True)
        row.operator('view3d.ke_shading_toggle', text="Flat/Smooth Toggle")
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "shading_tris", text="T", toggle=True)


classes = (
    UIModifiersModule,
    UISubDModule,
    KeSubd,
    KeSubDStep,
    KeSoloCutter,
    KeShowCutterMod,
    KeShadingToggle,
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
