import bpy
from bpy.types import Panel
from .._utils import get_prefs

from .pie_operators import KePieOps, KeCallPie, KeObjectOp, KeOverlays
from .ke_pie_subd import KePieSubd
from .ke_pie_fitprim import KePieFitPrim, KePieFitPrimAdd
from .ke_pie_snapping import KePieSnapping, KePieSnapAlign
from .ke_pie_fit2grid import KePieFit2Grid, KePieFit2GridMicro
from .ke_pie_multicut import KePieMultiCut
from .ke_pie_overlays import KePieOverlays
from .ke_pie_orientpivot import KePieOrientPivot
from .ke_pie_idmaterials import KePieMaterials
from .ke_pie_steprotate import KePieStepRotate
from .ke_pie_bookmarks import KePieBookmarks
from .ke_pie_misc import KePieMisc, KeMenuEditMesh
from .ke_pie_shading import KePieShading


class UIPieMenusModule(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_KEKIT"
    bl_label = "Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        m_modeling = k.m_modeling
        m_selection = k.m_selection
        m_bookmarks = k.m_bookmarks
        m_render = k.m_render

        layout = self.layout
        pie = layout.column()
        pie.operator("ke.call_pie", text="keShading", icon="DOT").name = "KE_MT_shading_pie"

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keSnapping", icon="DOT").name = "VIEW3D_MT_ke_pie_snapping"
        else:
            row.enabled = False
            row.label(text="keSnapping N/A")

        row = pie.row(align=True)
        if m_selection:
            row.operator("wm.call_menu_pie", text="keStepRotate", icon="DOT").name = "VIEW3D_MT_ke_pie_step_rotate"
        else:
            row.enabled = False
            row.label(text="keStepRotate N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keFit2Grid", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid"
            row.operator("wm.call_menu_pie", text="F2G Micro", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid_micro"
        else:
            row.enabled = False
            row.label(text="keFit2Grid N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="keOrientPivot", icon="DOT").name = "VIEW3D_MT_ke_pie_orientpivot"
        else:
            row.enabled = False
            row.label(text="keOrientPivot N/A")

        pie.operator("wm.call_menu_pie", text="keOverlays", icon="DOT").name = "VIEW3D_MT_ke_pie_overlays"

        row = pie.row(align=True)
        if m_modeling and m_selection:
            row.operator("wm.call_menu_pie", text="keSnapAlign", icon="DOT").name = "VIEW3D_MT_ke_pie_align"
        else:
            row.enabled = False
            row.label(text="keSnapAlign N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keFitPrim", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim"
            row.operator("wm.call_menu_pie", text="+Add", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim_add"
        else:
            row.enabled = False
            row.label(text="keFitPrim N/A")

        pie.operator("wm.call_menu_pie", text="keSubd", icon="DOT").name = "VIEW3D_MT_ke_pie_subd"

        row = pie.row(align=True)
        if m_render:
            row.operator("wm.call_menu_pie", text="keMaterials", icon="DOT").name = "VIEW3D_MT_PIE_ke_materials"
        else:
            row.enabled = False
            row.label(text="keMaterials N/A")

        row = pie.row(align=True)
        if m_bookmarks:
            row.operator("wm.call_menu_pie", text="View&CursorBookmarks",
                         icon="DOT").name = "VIEW3D_MT_ke_pie_vcbookmarks"
        else:
            row.enabled = False
            row.label(text="View&CursorBookmarks N/A")

        row = pie.row(align=True)
        if m_modeling:
            row.operator("wm.call_menu_pie", text="keMultiCut", icon="DOT").name = "VIEW3D_MT_ke_pie_multicut"
        else:
            row.enabled = False
            row.label(text="keMultiCut N/A")

        row = pie.row(align=True)
        row.operator("wm.call_menu_pie", text="keMisc", icon="DOT").name = "VIEW3D_MT_ke_pie_misc"


class UIPieMenusBlender(Panel):
    bl_idname = "UI_PT_M_PIEMENUS_BLENDER"
    bl_label = "Blender Default Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_PIEMENUS_KEKIT"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie().column()
        pie.operator("wm.call_menu_pie", text="Falloffs Pie",
                     icon="DOT").name = "VIEW3D_MT_proportional_editing_falloff_pie"
        pie.operator("wm.call_menu_pie", text="View Pie", icon="DOT").name = "VIEW3D_MT_view_pie"
        pie.operator("wm.call_menu_pie", text="Pivot Pie", icon="DOT").name = "VIEW3D_MT_pivot_pie"
        pie.operator("wm.call_menu_pie", text="Orientation Pie", icon="DOT").name = "VIEW3D_MT_orientations_pie"
        pie.operator("wm.call_menu_pie", text="Shading Pie", icon="DOT").name = "VIEW3D_MT_shading_pie"
        pie.operator("wm.call_menu_pie", text="Snap Pie", icon="DOT").name = "VIEW3D_MT_snap_pie"
        pie.operator("wm.call_menu_pie", text="UV: Snap Pie", icon="DOT").name = "IMAGE_MT_uvs_snap_pie"
        pie.separator()
        pie.operator("wm.call_menu_pie", text="Clip: Tracking", icon="DOT").name = "CLIP_MT_tracking_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Solving", icon="DOT").name = "CLIP_MT_solving_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Marker", icon="DOT").name = "CLIP_MT_marker_pie"
        pie.operator("wm.call_menu_pie", text="Clip: Reconstruction", icon="DOT").name = "CLIP_MT_reconstruction_pie"


classes = (
    UIPieMenusModule,
    UIPieMenusBlender,
    KeCallPie,
    KePieOps,
    KeOverlays,
    KeObjectOp,
    KePieSubd,
    KePieFitPrim,
    KePieFitPrimAdd,
    KePieSnapAlign,
    KePieSnapping,
    KePieFit2Grid,
    KePieFit2GridMicro,
    KePieMultiCut,
    KePieOverlays,
    KePieOrientPivot,
    KePieMaterials,
    KePieStepRotate,
    KePieBookmarks,
    KePieShading,
    KePieMisc,
    KeMenuEditMesh,
)


addon_keymaps = []


def register():
    k = get_prefs()
    if k.m_piemenus:
        for c in classes:
            bpy.utils.register_class(c)

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
            kmi = km.keymap_items.new(idname="ke.call_pie", type='ZERO', value='PRESS', ctrl=True, alt=True, shift=True)
            kmi.properties.name = "KE_MT_shading_pie"
            addon_keymaps.append((km, kmi))


def unregister():
    if "bl_rna" in UIPieMenusModule.__dict__:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        for c in reversed(classes):
            bpy.utils.unregister_class(c)
