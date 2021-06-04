bl_info = {
    "name": "keKIT",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 4, 3, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "warning": "",
    "description": "Modeling scripts etc",
    "doc_url": "https://artbykjell.com/wiki.html",
}

# -------------------------------------------------------------------------------------------------
# Note: This kit is very much WIP - ..and experimental.
# -------------------------------------------------------------------------------------------------

from . import _prefs
from . import ke_orient_and_pivot
from . import ke_cursor_fit
from . import ke_copyplus
from . import ke_merge_to_mouse
from . import ke_contextops
from . import ke_get_set_edit_mesh
from . import ke_pie_menus
from . import ke_unrotator
from . import ke_unbevel
from . import ke_itemize
from . import box_primitive
from . import ke_fitprim
from . import ke_misc
from . import ke_ground
from . import ke_direct_loop_cut
from . import ke_mouse_mirror_flip
from . import ke_quickmeasure
from . import ke_fit2grid
from . import ke_collision
from . import ke_zeroscale
from . import ke_quickscale
from . import ke_clean
from . import ke_lineararray
from . import ke_view_tools
from . import ke_id_material
from . import ke_mouse_axis_move
from . import ke_subd
from . import ke_snap_combo
from . import ke_radialarray
from . import ke_quick_origin_move
from . import ke_tt
from . import ke_bg_sync
from . import ke_frame_view
from . import ke_multicut

import bpy
from bpy.types import Panel
from urllib import request


version = 1.432
new_version = None

# -------------------------------------------------------------------------------------------------
# SUB MENU PANELS
# -------------------------------------------------------------------------------------------------
class VIEW3D_PT_kekit_selection(Panel):
    bl_label = "Select & Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("VIEW3D_OT_cursor_fit_selected_and_orient", text="Cursor Fit & Align")
        row.alignment="CENTER"
        row.prop(context.scene.kekit, "cursorfit", text="O&P")
        row = layout.row(align=True)
        row.operator("view3d.ke_quick_origin_move").mode = "MOVE"
        row.operator("view3d.ke_quick_origin_move", text="QOM AutoAxis").mode = "AUTOAXIS"
        col = layout.column(align=True)
        col.label(text="Align Object(s) To")
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_object_to_cursor', text="Cursor")
        row.operator('VIEW3D_OT_ke_align_object_to_active', text="Active Object").align = "BOTH"

        col.label(text="Align Origin(s) To")
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_origin_to_cursor', text="Cursor")
        row.operator('VIEW3D_OT_align_origin_to_selected', text="Selection")
        # row.operator('VIEW3D_OT_align_origin_to_selected', text="Sel.Loc").align = "LOCATION"
        row.operator('VIEW3D_OT_origin_to_selected', text="Sel.Loc")

        col.label(text="Align View To")
        row = col.row(align=True)
        row.operator('view3d.ke_view_align_toggle', text="Cursor").mode = 'CURSOR'
        row.operator('view3d.ke_view_align_toggle', text="Selected").mode = 'SELECTION'
        row.operator('view3d.ke_view_align_snap', text="Ortho Snap").contextual = False

        col.separator()
        col.operator('object.ke_straighten')
        col.operator('VIEW3D_OT_ke_swap', text="Swap Places")
        col.operator("MESH_OT_ke_select_boundary", text="Select Boundary (+Active)")
        col.operator('MESH_OT_ke_select_invert_linked', text="Select Inverted Linked")


class VIEW3D_PT_ke_bookmarks(Panel):
    bl_label = "Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    info_cursor = "Store & Recall Cursor Transforms (loc & rot)\n" \
               "Clear Slot: Reset cursor (zero loc & rot) and store\n" \
               "(Reset Cursor transform = Slot default)" \

    info_view = "Store & Recall Viewport Placement (persp/ortho, loc, rot)\n" \
               "Clear Slot: Use & Set a stored view to the same slot\n" \
               "(without moving the viewport camera)"

    info_combos = "Snapping Combos: Store & Restore snapping settings (Save kekit prefs!)\n" \
                  "Slot-combos are located in the standard Blender Snapping menu.\n" \
                  "Rename slots here."

    def draw(self, context):
        layout = self.layout

        # CURSOR BOOKMARKS
        row = layout.row(align=True)
        row.label(text="Cursor Bookmarks")
        row.operator('ke_popup.info', text="", icon="QUESTION", emboss=False).text = self.info_cursor

        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('VIEW3D_OT_ke_cursor_bookmark', text="", icon="IMPORT").mode = "SET6"
        if sum(bpy.context.scene.ke_cslot1) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="1", depress=True).mode = "USE1"
        if sum(bpy.context.scene.ke_cslot2) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="2", depress=True).mode = "USE2"
        if sum(bpy.context.scene.ke_cslot3) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="3", depress=True).mode = "USE3"
        if sum(bpy.context.scene.ke_cslot4) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="4", depress=True).mode = "USE4"
        if sum(bpy.context.scene.ke_cslot5) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="5", depress=True).mode = "USE5"
        if sum(bpy.context.scene.ke_cslot6) == 0:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('VIEW3D_OT_ke_cursor_bookmark', text="6", depress=True).mode = "USE6"

        # VIEW BOOKMARKS
        row = layout.row(align=True)
        row.label(text="View Bookmarks")
        row.operator('ke_popup.info', text="", icon="QUESTION", emboss=False).text = self.info_view

        q = bpy.context.scene.ke_query_props
        row = layout.grid_flow(row_major=True, columns=6, align=True)
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET1"
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET2"
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET3"
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET4"
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET5"
        row.operator('VIEW3D_OT_ke_view_bookmark', text="", icon="IMPORT").mode = "SET6"
        if sum(bpy.context.scene.ke_vslot1) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="1", depress=False).mode = "USE1"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="1", depress=True).mode = "USE1"
        if sum(bpy.context.scene.ke_vslot2) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="2", depress=False).mode = "USE2"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="2", depress=True).mode = "USE2"
        if sum(bpy.context.scene.ke_vslot3) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="3", depress=False).mode = "USE3"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="3", depress=True).mode = "USE3"
        if sum(bpy.context.scene.ke_vslot4) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="4", depress=False).mode = "USE4"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="4", depress=True).mode = "USE4"
        if sum(bpy.context.scene.ke_vslot5) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="5", depress=False).mode = "USE5"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="5", depress=True).mode = "USE5"
        if sum(bpy.context.scene.ke_vslot6) == 0:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="6", depress=False).mode = "USE6"
        else:
            row.operator('VIEW3D_OT_ke_view_bookmark', text="6", depress=True).mode = "USE6"

        sub = layout.row(align=True)
        sub.alignment="CENTER"
        sub.operator('VIEW3D_OT_ke_viewpos', text="Get").mode = "GET"
        sub.prop(q, "view_query", text="")
        sub.operator('VIEW3D_OT_ke_viewpos', text="Set").mode = "SET"

        row = layout.row()
        row.operator('view3d.ke_view_bookmark_cycle', text="Cycle View Bookmarks")

        # SNAPPING COMBOS
        row = layout.row(align=True)
        row.label(text="Snapping Combos")
        row.operator('ke_popup.info', text="", icon="QUESTION", emboss=False).text = self.info_combos
        col = layout.column(align=True)
        col.prop(bpy.context.scene.kekit, "snap_name1", text="") #, icon="KEYTYPE_JITTER_VEC"
        col.prop(bpy.context.scene.kekit, "snap_name2", text="") #, icon="KEYTYPE_EXTREME_VEC"
        col.prop(bpy.context.scene.kekit, "snap_name3", text="") #, icon="KEYTYPE_MOVING_HOLD_VEC"
        col.prop(bpy.context.scene.kekit, "snap_name4", text="") #, icon="KEYTYPE_KEYFRAME_VEC"


class VIEW3D_PT_kekit_modeling(Panel):
    bl_label = "Modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('view3d.ke_shading_toggle', text="Flat/Smooth Shading Toggle")
        col.operator('MESH_OT_merge_to_mouse', icon="MOUSE_MOVE", text="Merge To Mouse")

        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="MouseMirror").mode = "MIRROR"
        row.operator('VIEW3D_OT_ke_mouse_mirror_flip', icon="MOUSE_MOVE", text="MouseFlip").mode = "FLIP"

        col.operator('VIEW3D_OT_ke_ground', text="Ground or Center")
        col.operator('MESH_OT_ke_unbevel', text="Unbevel")

        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_collision', text="BBox").col_type = "BOX"
        row.operator('VIEW3D_OT_ke_collision', text="Convex Hull").col_type = "CONVEX"

        col.operator('MESH_OT_ke_zeroscale', text="ZeroScale to Cursor").orient_type = "CURSOR"

        col.separator(factor=0.5)

        row = col.row(align=True)
        row.scale_x = 0.85
        row.prop(context.scene.kekit, "qs_user_value", text="QScale")
        row.scale_x = 0.15
        row.prop(context.scene.kekit, "qs_unit_size", text="U", toggle=True)
        row.operator('VIEW3D_OT_ke_quickscale', text="X").user_axis = 0
        row.operator('VIEW3D_OT_ke_quickscale', text="Y").user_axis = 1
        row.operator('VIEW3D_OT_ke_quickscale', text="Z").user_axis = 2

        col.separator(factor=0.5)

        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_fit2grid', text="Fit2Grid")
        row.prop(context.scene.kekit, "fit2grid", text="Size:")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("VIEW3D_OT_ke_lineararray")

        row = col.row(align=True)
        row.operator("VIEW3D_OT_ke_radialarray")
        row2 = row.row(align=True)
        row2.alignment="RIGHT"
        row2.prop(context.scene.kekit, "ra_autoarrange", text="A", toggle=True)

        row = layout.row(align=True)
        row.operator('MESH_OT_ke_direct_loop_cut', text="Direct Loop Cut").mode = "DEFAULT"
        row.operator('MESH_OT_ke_direct_loop_cut', text="DLC & Slide").mode = "SLIDE"


class VIEW3D_PT_kekit_id_material(Panel):
    bl_label = "ID Materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Apply")
        row.label(text="Set Name")
        row.label(text="Set Color")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 1
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm01_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm01", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 2
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm02_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm02", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 3
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm03_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm03", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 4
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm04_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm04", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 5
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm05_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm05", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 6
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm06_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm06", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 7
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm07_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm07", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 8
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm08_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm08", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 9
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm09_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm09", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 10
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm10_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm10", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 11
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm11_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm11", text="")
        row = col.row(align=True)
        row.scale_x = 0.5
        row.operator('view3d.ke_id_material', text="Apply").m_id = 12
        row.scale_x = 1
        row.prop(context.scene.kekit, "idm12_name", text="")
        row.scale_x = 0.5
        row.prop(context.scene.kekit, "idm12", text="")


class VIEW3D_PT_Clean(Panel):
    bl_label = "Cleaning Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_clean', text="Macro Mesh Clean")

        col = layout.column(align=True)
        col.label(text="Macro Mesh Clean Options")
        box = col.box()
        boxcol = box.column(align=True)
        boxcol.prop(context.scene.kekit, "clean_doubles", text="Double Geo")
        # col.prop(context.scene.kekit, "clean_doubles_val", text="Doubles Threshold:")
        boxcol.prop(context.scene.kekit, "clean_loose", text="Loose Verts/Edges")
        boxcol.prop(context.scene.kekit, "clean_interior", text="Interior Faces")
        boxcol.prop(context.scene.kekit, "clean_degenerate", text="Degenerate Geo")
        # col.prop(context.scene.kekit, "clean_degenerate_val", text="Degenerate Threshold:")
        boxcol.prop(context.scene.kekit, "clean_collinear", text="Collinear Verts")
        col.separator(factor=0.5)
        col.label(text="Purge")
        box = col.box()
        boxrow = box.row(align=True)
        boxrow.operator('view3d.ke_purge', text="Mesh").block_type = "MESH"
        boxrow.operator('view3d.ke_purge', text="Material").block_type = "MATERIAL"
        boxrow.operator('view3d.ke_purge', text="Texture").block_type = "TEXTURE"
        boxrow.operator('view3d.ke_purge', text="Image").block_type = "IMAGE"
        boxcol = box.column(align=True)
        boxcol.operator('outliner.orphans_purge', text="Purge All Orphaned Data")
        col = layout.column(align=True)
        col.label(text="Selection Tools")
        col.operator('MESH_OT_ke_select_collinear', text="Select Collinear Verts")
        col = layout.column(align=True)
        col.label(text="Select Geo by (Vert Edge) Count:")
        row = layout.row(align=True)
        row.operator('VIEW3D_OT_ke_vert_count_select', text="0").sel_count = "0"
        row.operator('VIEW3D_OT_ke_vert_count_select', text="1").sel_count = "1"
        row.operator('VIEW3D_OT_ke_vert_count_select', text="2").sel_count = "2"
        row.operator('VIEW3D_OT_ke_vert_count_select', text="3").sel_count = "3"
        row.operator('VIEW3D_OT_ke_vert_count_select', text="4").sel_count = "4"
        row.operator('VIEW3D_OT_ke_vert_count_select', text="5+").sel_count = "5"


class VIEW3D_PT_Context_Tools(Panel):
    bl_label = "Context Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        tt_mode = bpy.context.scene.kekit.tt_mode
        tt_link = bpy.context.scene.kekit.tt_linkdupe

        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="TT Toggle")
        srow.operator("view3d.ke_tt", text="", icon='OBJECT_ORIGIN', depress=tt_mode[0]).mode = "TOGGLE_MOVE"
        srow.operator("view3d.ke_tt", text="", icon='EMPTY_AXIS', depress=tt_mode[1]).mode = "TOGGLE_ROTATE"
        srow.operator("view3d.ke_tt", text="", icon='AXIS_SIDE', depress=tt_mode[2]).mode = "TOGGLE_SCALE"
        scol.separator(factor=0.6)
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Move").mode = "MOVE"
        srow.operator('view3d.ke_tt', text="TT Rotate").mode = "ROTATE"
        srow.operator('view3d.ke_tt', text="TT Scale").mode = "SCALE"
        srow = scol.row(align=True)
        srow.operator('view3d.ke_tt', text="TT Dupe").mode = "DUPE"
        srow.operator('view3d.ke_tt', text="TT Mode Cycle").mode = "TOGGLE_CYCLE"
        srow = scol.row(align=True)
        srow.prop(context.scene.kekit, "tt_handles", text="Handles")
        srow.prop(context.scene.kekit, "tt_hide", text="Hide")
        srow.prop(context.scene.kekit, "tt_select", text="Select")
        scol.separator()
        scol.operator("view3d.ke_tt", text="Dupe Linked (Global)", icon='LINKED', depress=tt_link).mode = "TOGGLE_DUPE"
        col.separator()
        sub = col.box()
        scol = sub.column(align=True)
        srow = scol.row(align=True)
        srow.label(text="Mouse Axis",icon="EMPTY_AXIS")
        srow = scol.row(align=True)
        srow.operator('view3d.ke_mouse_axis_move', text="Move").mode = "MOVE"
        srow.operator('view3d.ke_mouse_axis_move', text="Rotate").mode = "ROT"
        srow.operator('view3d.ke_mouse_axis_move', text="Scale").mode = "SCL"
        srow = scol.row(align=True)
        srow.operator('view3d.ke_mouse_axis_move', text="Move Dupe").mode = "DUPE"
        srow.operator('view3d.ke_mouse_axis_move', text="Move Cursor").mode = "CURSOR"
        col.separator()

        sub = col.box()
        scol = sub.column(align=True)
        row = scol.row(align=True)
        row.label(text="View Plane", icon="AXIS_SIDE")
        row.operator("VIEW3D_OT_ke_vptransform", text="VPDupe").transform = "COPYGRAB"
        scol.separator(factor=0.6)
        row = scol.row(align=True)
        row.operator("VIEW3D_OT_ke_vptransform", text="VPGrab").transform = "TRANSLATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPRotate").transform = "ROTATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPResize").transform = "RESIZE"
        row = scol.row()
        row.prop(context.scene.kekit, "vptransform", text="VPAG")
        row.prop(context.scene.kekit, "loc_got", text="GGOT")
        row.prop(context.scene.kekit, "rot_got", text="RGOT")
        row.prop(context.scene.kekit, "scl_got", text="SGOT")

        col = layout.column(align=True)
        col.operator('view3d.ke_view_align_snap', text="View Align Snap Contextual").contextual = True
        col.operator("screen.ke_frame_view", text="Frame All or Selected")
        col.operator('MESH_OT_ke_contextbevel', text="Context Bevel")
        row = col.row(align=True)
        row.operator('MESH_OT_ke_contextextrude', text="Context Extrude")
        row.alignment = "CENTER"
        row.prop(bpy.context.scene.kekit, "tt_extrude", text="TT")
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_contextdelete', text="Context Delete")
        row.alignment = "CENTER"
        row.prop(bpy.context.scene.kekit, "h_delete", text="H")
        col.operator('MESH_OT_ke_contextdissolve', text="Context Dissolve")
        col.operator('VIEW3D_OT_ke_contextselect', text="Context Select")
        col.operator('VIEW3D_OT_ke_contextselect_extend', text="Context Select Extend")
        col.operator('VIEW3D_OT_ke_contextselect_subtract', text="Context Select Subtract")
        col.operator('MESH_OT_ke_bridge_or_fill', text="Bridge or Fill")
        col.operator('MESH_OT_ke_maya_connect', text="Maya Connect")
        col.operator('MESH_OT_ke_triple_connect_spin', text="Triple Connect Spin")
        col.operator('MESH_OT_ke_contextslide')


# PIE MENUS

class VIEW3D_PT_BlenderPieMenus(Panel):
    bl_label = "Blender Default Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_PieMenus"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie().column()
        pie.operator("wm.call_menu_pie", text="Falloffs Pie", icon="DOT").name = "VIEW3D_MT_proportional_editing_falloff_pie"
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


class VIEW3D_PT_PieMenus(Panel):
    bl_label = "Pie Menus"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        # layout.label(text="keKit Pie Menus")
        pie = layout.menu_pie().column()
        pie.operator("ke.call_pie", text="keShading", icon="DOT").name = "KE_MT_shading_pie"
        pie.operator("wm.call_menu_pie", text="keSnapping", icon="DOT").name = "VIEW3D_MT_ke_pie_snapping"
        pie.operator("wm.call_menu_pie", text="keStepRotate", icon="DOT").name = "VIEW3D_MT_ke_pie_step_rotate"
        pie.operator("wm.call_menu_pie", text="keFit2Grid", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid"
        pie.operator("wm.call_menu_pie", text="keFit2Grid Micro", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid_micro"
        pie.operator("wm.call_menu_pie", text="keOrientPivot", icon="DOT").name = "VIEW3D_MT_ke_pie_orientpivot"
        pie.operator("wm.call_menu_pie", text="keOverlays", icon="DOT").name = "VIEW3D_MT_ke_pie_overlays"
        pie.operator("wm.call_menu_pie", text="keSnapAlign", icon="DOT").name = "VIEW3D_MT_ke_pie_align"
        pie.operator("wm.call_menu_pie", text="keFitPrim", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim"
        pie.operator("wm.call_menu_pie", text="keSubd", icon="DOT").name = "VIEW3D_MT_ke_pie_subd"
        pie.operator("wm.call_menu_pie", text="keMaterials", icon="DOT").name = "VIEW3D_MT_PIE_ke_materials"
        pie.operator("wm.call_menu_pie", text="View&CursorBookmarks", icon="DOT").name = "VIEW3D_MT_ke_pie_vcbookmarks"
        pie.operator("wm.call_menu_pie", text="keMulticut", icon="DOT").name = "VIEW3D_MT_ke_pie_multicut"


class VIEW3D_PT_ke_snapcombos(Panel):
    bl_label = "Snapping Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = "VIEW3D_PT_snapping"

    def draw(self, context):
        layout = self.layout
        layout.separator(factor=0.3)
        row = layout.row(align=True)
        row.operator('view3d.ke_snap_combo', icon="IMPORT", text=" ").mode = "GET1"
        row.operator('view3d.ke_snap_combo', text="1").mode = "SET1"
        row.separator(factor=0.7)
        row.operator('view3d.ke_snap_combo', icon="IMPORT", text=" ").mode = "GET2"
        row.operator('view3d.ke_snap_combo', text="2").mode = "SET2"
        row.separator(factor=0.7)
        row.operator('view3d.ke_snap_combo', icon="IMPORT", text=" ").mode = "GET3"
        row.operator('view3d.ke_snap_combo', text="3").mode = "SET3"
        row.separator(factor=0.7)
        row.operator('view3d.ke_snap_combo', icon="IMPORT", text=" ").mode = "GET4"
        row.operator('view3d.ke_snap_combo', text="4").mode = "SET4"


class VIEW3D_PT_OPC(Panel):
    bl_label = "Orientation & Pivot Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_ke_bookmarks"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class VIEW3D_PT_OPC1(Panel):
    bl_label = "O&P Combo 1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        name = bpy.context.scene.kekit.opc1_name
        toggle = bpy.context.scene.ke_query_props.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "opc1_name", text="")
            row.alignment="CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon="KEYTYPE_JITTER_VEC", text="%s" % name).combo="1"
            row.alignment="CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC1 Object Mode")
        col.prop(context.scene.kekit, 'opc1_obj_o', text="Orient")
        col.prop(context.scene.kekit, 'opc1_obj_p', text="Pivot")
        col.label(text="OPC1 Edit Mode")
        col.prop(context.scene.kekit, 'opc1_edit_o', text="Orientation")
        col.prop(context.scene.kekit, 'opc1_edit_p', text="Pivot")


class VIEW3D_PT_OPC2(Panel):
    bl_label = "O&P Combo 2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        name = bpy.context.scene.kekit.opc2_name
        toggle = bpy.context.scene.ke_query_props.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "opc2_name", text="")
            row.alignment="CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon="KEYTYPE_EXTREME_VEC", text="%s" % name).combo="2"
            row.alignment="CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC2 Object Mode")
        col.prop(context.scene.kekit, 'opc2_obj_o', text="Orient")
        col.prop(context.scene.kekit, 'opc2_obj_p', text="Pivot")
        col.label(text="OPC2 Edit Mode")
        col.prop(context.scene.kekit, 'opc2_edit_o', text="Orientation")
        col.prop(context.scene.kekit, 'opc2_edit_p', text="Pivot")


class VIEW3D_PT_OPC3(Panel):
    bl_label = "O&P Combo 3"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        name = bpy.context.scene.kekit.opc3_name
        toggle = bpy.context.scene.ke_query_props.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "opc3_name", text="")
            row.alignment = "CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon="KEYTYPE_MOVING_HOLD_VEC", text="%s" % name).combo = "3"
            row.alignment = "CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC3 Object Mode")
        col.prop(context.scene.kekit, 'opc3_obj_o', text="Orient")
        col.prop(context.scene.kekit, 'opc3_obj_p', text="Pivot")
        col.label(text="OPC3 Edit Mode")
        col.prop(context.scene.kekit, 'opc3_edit_o', text="Orientation")
        col.prop(context.scene.kekit, 'opc3_edit_p', text="Pivot")


class VIEW3D_PT_OPC4(Panel):
    bl_label = "O&P Combo 4"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        name = bpy.context.scene.kekit.opc4_name
        toggle = bpy.context.scene.ke_query_props.toggle

        layout = self.layout
        row = layout.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "opc4_name", text="")
            row.alignment = "CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)
        else:
            row.operator('view3d.ke_opc', icon="KEYTYPE_KEYFRAME_VEC", text="%s" % name).combo = "4"
            row.alignment = "CENTER"
            row.prop(bpy.context.scene.ke_query_props, "toggle", text="Name", toggle=True)

        col = layout.column(align=True)
        col.label(text="OPC4 Object Mode")
        col.prop(context.scene.kekit, 'opc4_obj_o', text="Orient")
        col.prop(context.scene.kekit, 'opc4_obj_p', text="Pivot")
        col.label(text="OPC4 Edit Mode")
        col.prop(context.scene.kekit, 'opc4_edit_o', text="Orientation")
        col.prop(context.scene.kekit, 'opc4_edit_p', text="Pivot")


# -------------------------------------------------------------------------------------------------
# SUB TOOL PANELS (NOT SEPARATE PANEL MENU TABS)
# -------------------------------------------------------------------------------------------------

class VIEW3D_PT_MultiCut(Panel):
    bl_label = "MultiCut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def get_props(self, preset="0"):
        p = bpy.context.scene.kekit.mc_prefs[:]
        v1, v2, v3, v4 = 0, 0, 0, 0
        if preset == "0":
            v1, v2, v3, v4 = p[0], p[1], p[2], p[3]
        elif preset == "1":
            v1, v2, v3, v4 = p[4], p[5], p[6], p[7]
        elif preset == "2":
            v1, v2, v3, v4 = p[8], p[9], p[10], p[11]
        elif preset == "3":
            v1, v2, v3, v4 = p[12], p[13], p[14], p[15]
        elif preset == "4":
            v1, v2, v3, v4 = p[16], p[17], p[18], p[19]
        elif preset == "5":
            v1, v2, v3, v4 = p[20], p[21], p[22], p[23]
        elif preset == "6":
            v1, v2, v3, v4 = p[24], p[25], p[26], p[27]
        elif preset == "7":
            v1, v2, v3, v4 = p[28], p[29], p[30], p[31]
        return v1, str(int(v2)), v3, bool(v4)

    def draw(self, context):
        toggle = bpy.context.scene.ke_query_props.toggle

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_x = 1
        row.prop(context.scene.kekit, "mc_relative", text="")
        row.scale_x = 0.25
        row.prop(context.scene.kekit, "mc_center", text="")
        row.scale_x = 1
        row.prop(context.scene.kekit, "mc_fixed", text="")

        col = layout.column(align=False)

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name0", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name0)
            v1,v2,v3,v4 = self.get_props(preset="0")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC1")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 0

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name1", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name1)
            v1,v2,v3,v4 = self.get_props(preset="1")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC2")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 1

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name2", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name2)
            v1,v2,v3,v4 = self.get_props(preset="2")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC3")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 2

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name3", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name3)
            v1,v2,v3,v4 = self.get_props(preset="3")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC4")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 3

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name4", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name4)
            v1,v2,v3,v4 = self.get_props(preset="4")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC5")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 4

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name5", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name5)
            v1,v2,v3,v4 = self.get_props(preset="5")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC6")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 5

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name6", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name6)
            v1,v2,v3,v4 = self.get_props(preset="6")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC7")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 6

        row = col.row(align=True)
        if toggle:
            row.prop(bpy.context.scene.kekit, "mc_name7", text="")
        else:
            op = row.operator('MESH_OT_ke_multicut', text="%s" % bpy.context.scene.kekit.mc_name7)
            v1,v2,v3,v4 = self.get_props(preset="7")
            op.o_relative = v1
            op.o_center = v2
            op.o_fixed = v3
            op.using_fixed = v4
            op.preset = "SET"

        row.scale_x = 0.35
        row.label(text=" MC8")
        row.scale_x = 1
        row.operator('ke.mcprefs', text="", icon="IMPORT").preset = 7

        row = col.row(align=True)
        row.prop(bpy.context.scene.ke_query_props, "toggle", text="Manual Rename", toggle=True)


class VIEW3D_PT_FitPrim(Panel):
    bl_label = "FitPrim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cube", icon="MESH_CUBE").ke_fitprim_option = "BOX"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cylinder", icon="MESH_CYLINDER").ke_fitprim_option = "CYL"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Plane", icon="MESH_PLANE").ke_fitprim_option = "PLANE"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Sphere", icon="MESH_UVSPHERE").ke_fitprim_option = "SPHERE"
        col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim QuadSphere", icon="SPHERE").ke_fitprim_option = "QUADSPHERE"
        col.separator()
        col.label(text="Options")
        col.prop(context.scene.kekit, "fitprim_unit", text="No-sel Unit Size")
        col.separator()
        col.prop(context.scene.kekit, "fitprim_sides", text="Cylinder Default Sides:")
        col.prop(context.scene.kekit, "fitprim_modal", text="Modal Cylinder")
        col.prop(context.scene.kekit, "fitprim_sphere_seg", text="Sphere Segments")
        col.prop(context.scene.kekit, "fitprim_sphere_ring", text="Sphere Rings")
        col.prop(context.scene.kekit, "fitprim_quadsphere_seg", text="QuadSphere Div")
        col.prop(context.scene.kekit, "fitprim_select", text="Select Result (Edit Mesh)")
        col.prop(context.scene.kekit, "fitprim_item", text="Make Object")


class VIEW3D_PT_Unrotator(Panel):
    bl_label = "Unrotator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator", icon="ORIENTATION_NORMAL").ke_unrotator_option = "DEFAULT"
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator Duplicate", icon="LINKED").ke_unrotator_option = "DUPE"
        col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator RotOnly", icon="ORIENTATION_LOCAL").ke_unrotator_option = "NO_LOC"
        col.separator()
        col.label(text="Options")
        # col.prop(context.scene.kekit, "unrotator_reset", text="Auto-Reset")
        col.prop(context.scene.kekit, "unrotator_connect", text="Auto-Select Linked")
        col.prop(context.scene.kekit, "unrotator_nolink", text="Object Duplicate Unlinked")
        col.prop(context.scene.kekit, "unrotator_nosnap", text="No Object Modal Snapping")
        col.prop(context.scene.kekit, "unrotator_invert", text="Invert Rotation")
        col.prop(context.scene.kekit, "unrotator_center", text="Center on Face")


class VIEW3D_PT_Subd_Toggle(Panel):
    bl_label = "Subd Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('view3d.ke_subd_step', text="Step VP Lv +1").step_up = True
        row.operator('view3d.ke_subd_step', text="Step VP Lv -1").step_up = False
        row = col.row(align=True)
        row.operator('view3d.ke_subd', text="Set VP Lv").level_mode = "VIEWPORT"
        row.operator('view3d.ke_subd', text="Set Render Lv").level_mode = "RENDER"
        col.separator()
        col.operator('view3d.ke_subd', text="SubD Toggle").level_mode = "TOGGLE"
        # col.separator()
        col.label(text="Options")
        row = col.row(align=True)
        row.prop(context.scene.kekit, "vp_level", text="VP Lv")
        row.prop(context.scene.kekit, "render_level", text="Render Lv")
        col.separator()
        row = col.row(align=True)
        row.alignment = "LEFT"
        row.label(text="Boundary")
        row.prop(context.scene.kekit, "boundary_smooth", text="")
        col.separator(factor=0.5)
        col.prop(context.scene.kekit, "limit_surface", text="Use Limit Surface")
        col.prop(context.scene.kekit, "flat_edit", text="Flat Shade when off")
        col.prop(context.scene.kekit, "optimal_display", text="Use Optimal Display")
        col.prop(context.scene.kekit, "on_cage", text="On Cage")


# -------------------------------------------------------------------------------------------------
# MENU
# -------------------------------------------------------------------------------------------------

class VIEW3D_PT_kekit(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_label = 'keKit v%s' % version
    # bl_options = {'HIDE_HEADER'}


    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
        row = layout.row(align=True)
        if new_version is not None:
            row.scale_x = 0.6
            row.operator("wm.url_open", text="%s" %str(new_version)[2:], icon="ERROR").url = "https://artbykjell.com/blender.html"
            row.separator()
        row.scale_x = 1
        row.operator('VIEW3D_OT_ke_prefs_save', text="", icon="FILE_CACHE")
        row.separator()

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=False)
        row.alignment="CENTER"
        row.operator('VIEW3D_OT_ke_selmode', text="", icon="VERTEXSEL").edit_mode = "VERT"
        row.operator('VIEW3D_OT_ke_selmode', text="", icon="EDGESEL").edit_mode = "EDGE"
        row.operator('VIEW3D_OT_ke_selmode', text="", icon="FACESEL").edit_mode = "FACE"
        row.operator('VIEW3D_OT_ke_selmode', text="", icon="OBJECT_DATAMODE").edit_mode = "OBJECT"
        row.separator()
        row.prop(context.scene.kekit, "selmode_mouse", text="")
        row.operator('VIEW3D_OT_ke_spacetoggle', text="", icon="MOUSE_MOVE")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_copyplus', text="Cut+").mode = "CUT"
        row.operator('VIEW3D_OT_ke_copyplus', text="Copy+").mode = "COPY"
        row.operator('VIEW3D_OT_ke_copyplus', text="Paste+").mode = "PASTE"
        row.separator()
        row.prop(context.scene.kekit, "paste_merge", text="")
        row = col.row(align=True)
        row.operator('MESH_OT_ke_extract_and_edit', text="Extract&Edit").copy = False
        row.operator('MESH_OT_ke_extract_and_edit', text="E&E Copy").copy = True
        row = col.row(align=True)
        row.operator('MESH_OT_ke_itemize', text="Itemize").mode = "DEFAULT"
        row.operator('MESH_OT_ke_itemize', text="DupeItemize").mode = "DUPE"

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_get_set_editmesh', icon="MOUSE_MOVE", text="Get&Set Edit")
        row2 = row.row(align=True)
        row2.alignment="RIGHT"
        row2.operator('VIEW3D_OT_ke_get_set_editmesh', text="Extend").extend = True
        row2.prop(context.scene.kekit, "getset_ep", text="")

        col.operator('VIEW3D_OT_ke_get_set_material', icon="MOUSE_MOVE", text="Get&Set Material")
        col.separator(factor=0.5)
        row = col.row(align=True)
        row.operator('VIEW3D_OT_ke_quickmeasure', icon="DRIVER_DISTANCE", text="QuickMeasure").qm_start = "DEFAULT"
        row.scale_x = 0.65
        row.operator('VIEW3D_OT_ke_quickmeasure', text="QM Freeze").qm_start = "SEL_SAVE"
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('screen.ke_render_visible', icon="RENDER_STILL", text="Render Visible")
        row2 = row.row(align=True)
        row2.alignment="RIGHT"
        row2.separator()
        row2.prop(context.scene.kekit, "renderslotcycle", text="SC")
        # col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('screen.ke_render_slotcycle', icon="RENDER_STILL", text="Render Slot Cycle")
        row2 = row.row(align=True)
        row2.alignment="RIGHT"
        row2.separator()
        row2.prop(context.scene.kekit, "renderslotfullwrap", text="FW")
        col.separator(factor=0.5)
        col.operator('view3d.ke_bg_sync', icon="SHADING_TEXTURE")

# -------------------------------------------------------------------------------------------------
# Prefs & Properties
# -------------------------------------------------------------------------------------------------

class ke_query_props(bpy.types.PropertyGroup):
    view_query: bpy.props.StringProperty(default=" N/A ")
    toggle: bpy.props.BoolProperty(default=False)

panels = (
        VIEW3D_PT_kekit,
        VIEW3D_PT_kekit_modeling,
        VIEW3D_PT_Context_Tools,
        VIEW3D_PT_OPC,
        VIEW3D_PT_PieMenus,
        )

def update_panel(self, context):
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, "Error", e))
        pass


def version_check():
    v = 0
    try:
        v = float(request.urlopen("https://artbykjell.com/bversion.html").read())
    except:
        pass
    if v > version:
        global new_version
        new_version = v

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    ke_query_props,
    VIEW3D_PT_kekit,
    VIEW3D_PT_ke_bookmarks,
    VIEW3D_PT_kekit_selection,
    VIEW3D_PT_kekit_modeling,
    VIEW3D_PT_kekit_id_material,
    VIEW3D_PT_Clean,
    VIEW3D_PT_MultiCut,
    VIEW3D_PT_Subd_Toggle,
    VIEW3D_PT_Unrotator,
    VIEW3D_PT_FitPrim,
    VIEW3D_PT_Context_Tools,
    VIEW3D_PT_OPC,
    VIEW3D_PT_OPC1,
    VIEW3D_PT_OPC2,
    VIEW3D_PT_OPC3,
    VIEW3D_PT_OPC4,
    VIEW3D_PT_PieMenus,
    VIEW3D_PT_BlenderPieMenus,
    VIEW3D_PT_ke_snapcombos,
    )

modules = (
    _prefs,
    ke_orient_and_pivot,
    ke_cursor_fit,
    ke_copyplus,
    ke_merge_to_mouse,
    ke_contextops,
    ke_get_set_edit_mesh,
    ke_pie_menus,
    ke_unrotator,
    ke_unbevel,
    ke_itemize,
    box_primitive,
    ke_fitprim,
    ke_misc,
    ke_ground,
    ke_direct_loop_cut,
    ke_quickmeasure,
    ke_fit2grid,
    ke_collision,
    ke_zeroscale,
    ke_quickscale,
    ke_clean,
    ke_lineararray,
    ke_radialarray,
    ke_view_tools,
    ke_id_material,
    ke_mouse_axis_move,
    ke_subd,
    ke_snap_combo,
    ke_mouse_mirror_flip,
    ke_quick_origin_move,
    ke_tt,
    ke_bg_sync,
    ke_frame_view,
    ke_multicut
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.ke_query_props = bpy.props.PointerProperty(type=ke_query_props, name="Input")

    for m in modules:
        m.register()

    version_check()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for m in modules:
        m.unregister()

    try:
        del bpy.types.Scene.ke_query_props

    except Exception as e:
        print('unregister fail:\n', e)
        pass

if __name__ == "__main__":
    register()
