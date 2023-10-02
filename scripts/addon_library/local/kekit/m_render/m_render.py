import bpy

from .ke_bgsync import KeBgSync
from .ke_render_slotcycle import KeRenderSlotCycle
from .ke_render_visible import KeRenderVisible
from .m_id_materials import KeIDMaterial, UIIDMaterialsModule
from .ke_get_set_material import KeGetSetMaterial
from .ke_syncvpmaterial import KeSyncviewportMaterial

from .._ui import pcoll
from .._utils import get_prefs


class UIRenderModule(bpy.types.Panel):
    bl_idname = "UI_PT_M_RENDER"
    bl_label = "Render & Shade"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator('screen.ke_render_visible', icon="RENDER_STILL", text="Render Visible")
        if k.renderslotcycle:
            row.prop(k, "renderslotcycle", text="", toggle=True, icon="CHECKMARK")
        else:
            row.prop(k, "renderslotcycle", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)

        row = col.row(align=True)
        row.operator('screen.ke_render_slotcycle', icon="RENDER_STILL", text="Render Slot Cycle")
        if k.renderslotfullwrap:
            row.prop(k, "renderslotfullwrap", text="", toggle=True, icon="CHECKMARK")
        else:
            row.prop(k, "renderslotfullwrap", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)

        col.operator('view3d.ke_bg_sync', icon="SHADING_TEXTURE")
        col.operator('view3d.ke_get_set_material', icon="MOUSE_MOVE", text="Get&Set Material")


def draw_syncvpbutton(self, context):
    layout = self.layout
    row = layout.row()
    row.use_property_split = True
    row.operator("view3d.ke_syncvpmaterial", icon="COLOR")


classes = (
    UIRenderModule,
    UIIDMaterialsModule,
    KeRenderVisible,
    KeRenderSlotCycle,
    KeBgSync,
    KeIDMaterial,
    KeGetSetMaterial,
    KeSyncviewportMaterial,
)


def register():
    k = get_prefs()

    if k.m_render:
        for c in classes:
            bpy.utils.register_class(c)

        if k.material_extras:
            bpy.types.EEVEE_MATERIAL_PT_surface.prepend(draw_syncvpbutton)


def unregister():
    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(draw_syncvpbutton)
    except Exception as e:
        print('keKit Draw SyncVpMaterial Button Unregister: ', e)
        pass

    if "bl_rna" in UIRenderModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
