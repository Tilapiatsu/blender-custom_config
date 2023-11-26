import bpy
from bpy.types import Panel

from .ops.ke_check_snapping import KeCheckSnapping
from .ops.ke_clean import KeClean
from .ops.ke_purge import KePurge
from .ops.ke_select_collinear import KeSelectCollinear
from .ops.ke_select_flippednormal import KeSelectFlippedNormal
from .ops.ke_select_occluded_verts import KeSelectOccludedVerts
from .ops.ke_vertcountselect import KeVertCountSelect

from ._utils import get_prefs


class UICleanUpToolsModule(Panel):
    bl_idname = "UI_PT_M_CLEANUPTOOLS"
    bl_label = "Clean-Up Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        col.label(text="Macro Mesh Clean")
        row = col.row(align=True)
        row.operator('view3d.ke_clean', text="Select").select_only = True
        row.operator('view3d.ke_clean', text="Clean").select_only = False
        col.separator(factor=0.5)
        col.prop(k, "clean_doubles")
        col.prop(k, "clean_loose")
        col.prop(k, "clean_interior")
        col.prop(k, "clean_degenerate")
        col.prop(k, "clean_collinear")
        col.prop(k, "clean_tinyedge")
        col.prop(k, "clean_tinyedge_val")
        col.prop(k, "clean_collinear_val")
        col = layout.column(align=True)

        col.label(text="Purge")
        boxrow = col.row(align=True)
        boxrow.operator('view3d.ke_purge', text="Mesh").block_type = "MESH"
        boxrow.operator('view3d.ke_purge', text="Material").block_type = "MATERIAL"
        boxrow.operator('view3d.ke_purge', text="Texture").block_type = "TEXTURE"
        boxrow.operator('view3d.ke_purge', text="Image").block_type = "IMAGE"
        col.operator('outliner.orphans_purge', text="Purge All Orphaned Data")

        col.label(text="Selection Tools")
        col.operator('mesh.ke_select_collinear')
        col.operator('mesh.ke_select_flipped_normal')
        col.operator('view3d.ke_check_snapping')
        col.operator('view3d.ke_select_occluded_verts')

        col.label(text="Select Elements by Vert Count:")
        row = col.row(align=True)
        row.operator('view3d.ke_vert_count_select', text="0").sel_count = "0"
        row.operator('view3d.ke_vert_count_select', text="1").sel_count = "1"
        row.operator('view3d.ke_vert_count_select', text="2").sel_count = "2"
        row.operator('view3d.ke_vert_count_select', text="3").sel_count = "3"
        row.operator('view3d.ke_vert_count_select', text="4").sel_count = "4"
        row.operator('view3d.ke_vert_count_select', text="5+").sel_count = "5"


classes = (
    KeCheckSnapping,
    KeClean,
    KePurge,
    KeSelectCollinear,
    KeSelectFlippedNormal,
    KeSelectOccludedVerts,
    KeVertCountSelect,
    UICleanUpToolsModule,
)


def register():
    k = get_prefs()
    if k.m_cleanup:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UICleanUpToolsModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
