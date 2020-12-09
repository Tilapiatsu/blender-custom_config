bl_info = {
    "name": "keKIT",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 3, 8, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "warning": "",
    "description": "Modeling scripts etc",
    "wiki_url": "http://artbykjell.com",
    "category": "Mesh",
}
# -------------------------------------------------------------------------------------------------
# Note: This kit is very much WIP - ..and experimental.
# -------------------------------------------------------------------------------------------------
# from ._prefs import get_prefs, write_prefs, VIEW3D_OT_ke_prefs_save

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
from . import ke_mouse_flip
from . import ke_mouse_mirror
from . import ke_quickmeasure
from . import ke_fit2grid
from . import ke_collision
from . import ke_zeroscale
from . import ke_quickscale
from . import ke_clean
from . import ke_lineararray

import bpy
from bpy.types import Panel

nfo = "keKit v1.384"
# -------------------------------------------------------------------------------------------------
# SUB MENU PANELS
# -------------------------------------------------------------------------------------------------
class VIEW3D_PT_kekit_selection(Panel):
    bl_label = "Select & Align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.alignment="CENTER"
        row.operator("VIEW3D_OT_cursor_fit_selected_and_orient", text="Cursor Fit & Align")
        row.prop(context.scene.kekit, "cursorfit", text="O&P")

        col = layout.column(align=True)
        col.label(text="Align Object(s) To")
        row = col.row(align=True)
        row.alignment="CENTER"
        row.operator('VIEW3D_OT_ke_object_to_cursor', text="Cursor")
        row.operator('VIEW3D_OT_ke_align_object_to_active', text="Active Object").align = "BOTH"

        col.label(text="Align Origin(s) To")
        row = col.row(align=True)
        row.alignment="CENTER"
        row.operator('VIEW3D_OT_ke_origin_to_cursor', text="Cursor")
        row.operator('VIEW3D_OT_align_origin_to_selected', text="Selection")
        row.operator('VIEW3D_OT_origin_to_selected', text="Sel.Loc")

        col.separator()
        col.operator('VIEW3D_OT_ke_swap', text="Swap Places")
        col.operator("MESH_OT_ke_select_boundary", text="Select Boundary (+Active)")
        col.operator('MESH_OT_ke_select_invert_linked', text="Select Inverted Linked")
        col.operator('view3d.ke_view_align_toggle')
        col.operator('view3d.ke_view_align_snap').contextual = False


class VIEW3D_PT_ke_cursorbookmarks(Panel):
    bl_label = "Cursor Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_selection"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
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


class VIEW3D_PT_ke_viewbookmarks(Panel):
    bl_label = "View Bookmarks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_selection"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        q = bpy.context.scene.ke_query_props
        layout = self.layout
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
        # srow = sub.row()

class VIEW3D_PT_kekit_modeling(Panel):
    bl_label = "Modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        # col.operator('MESH_OT_primitive_box_add', text="Add Box Primitive", icon='MESH_CUBE')
        # col.separator()
        col.operator('MESH_OT_merge_to_mouse', icon="MOUSE_MOVE", text="Merge To Mouse")
        col.operator('VIEW3D_OT_ke_ground', text="Ground or Center")
        col.operator('MESH_OT_ke_unbevel', text="Unbevel")
        col.operator('MESH_OT_ke_zeroscale', text="ZeroScale to Cursor").orient_type = "CURSOR"

        row = layout.row(align=True)
        row.operator('MESH_OT_ke_itemize', text="Itemize").mode = "DEFAULT"
        row.operator('MESH_OT_ke_itemize', text="Dupe & Itemize").mode = "DUPE"

        col = layout.column(align=True)
        col.operator('MESH_OT_ke_extract_and_edit', text="Extract & Edit")
        # col.separator()
        r = layout.row(align=True)
        r.operator('MESH_OT_ke_direct_loop_cut', text="DLoopCut&Slide").mode = "SLIDE"
        r.operator('MESH_OT_ke_direct_loop_cut', text="DirectLoopCut").mode = "DEFAULT"

        row = layout.row(align=True)
        row.operator('VIEW3D_OT_ke_collision', text="BBox").col_type = "BOX"
        row.operator('VIEW3D_OT_ke_collision', text="Convex Hull").col_type = "CONVEX"

        col = layout.row(align=True)
        col.operator('VIEW3D_OT_ke_fit2grid', text="Fit2Grid")
        col.prop(context.scene.kekit, "fit2grid", text="Size:")

        row = layout.row(align=True)
        row.operator('VIEW3D_OT_ke_lineararray')


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
        col.label(text="Cleaning Options")
        col.prop(context.scene.kekit, "clean_doubles", text="Double Geo")
        # col.prop(context.scene.kekit, "clean_doubles_val", text="Doubles Threshold:")
        col.prop(context.scene.kekit, "clean_loose", text="Loose Verts/Edges")
        col.prop(context.scene.kekit, "clean_interior", text="Interior Faces")
        col.prop(context.scene.kekit, "clean_degenerate", text="Degenerate Geo")
        # col.prop(context.scene.kekit, "clean_degenerate_val", text="Degenerate Threshold:")
        col.prop(context.scene.kekit, "clean_collinear", text="Collinear Verts")
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



class VIEW3D_PT_VPContextual(Panel):
    bl_label = "ViewPlane Contextual"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_Context_Tools"
    # bl_options = {'DEFAULT_OPEN'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row()
        row.operator("VIEW3D_OT_ke_vptransform", text="VPGrab").transform = "TRANSLATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPRotate").transform = "ROTATE"
        row.operator("VIEW3D_OT_ke_vptransform", text="VPResize").transform = "RESIZE"
        sub = col.column()
        sub.alignment = 'CENTER'
        sub.separator()
        sub.operator("VIEW3D_OT_ke_vptransform", text="VPDupeMove").transform = "COPYGRAB"
        sub = col.row()
        sub.alignment = 'CENTER'
        sub.prop(context.scene.kekit, "vptransform", text="VP Always Global")


class VIEW3D_PT_Context_Tools(Panel):
    bl_label = "Context Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('MESH_OT_ke_contextbevel', text="Context Bevel")
        col.operator('MESH_OT_ke_contextextrude', text="Context Extrude")
        col.operator('VIEW3D_OT_ke_contextdelete', text="Context Delete")
        col.operator('MESH_OT_dissolve_mode', text="Context Dissolve (Blender)")
        col.operator('MESH_OT_ke_contextdissolve', text="Context Dissolve")
        col.operator('VIEW3D_OT_ke_contextselect', text="Context Select")
        col.operator('VIEW3D_OT_ke_contextselect_extend', text="Context Select Extend")
        col.operator('VIEW3D_OT_ke_contextselect_subtract', text="Context Select Subtract")
        col.operator('MESH_OT_ke_bridge_or_fill', text="Bridge or Fill")
        col.operator('MESH_OT_ke_maya_connect', text="Maya Connect")
        col.operator('MESH_OT_ke_triple_connect_spin', text="Triple Connect Spin")
        col.operator("VIEW3D_OT_ke_frame_view", text="Frame All or Selected")
        col.operator('MESH_OT_ke_contextslide')
        col.operator('view3d.ke_view_align_snap', text="View Align Snap Contextual").contextual = True



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
        layout.label(text="ke Pie Menus")
        pie = layout.menu_pie().column()
        pie.operator("wm.call_menu_pie", text="keSnapping", icon="DOT").name = "VIEW3D_MT_ke_pie_snapping"
        pie.operator("wm.call_menu_pie", text="bSnapping", icon="DOT").name = "VIEW3D_MT_bsnapping"
        pie.operator("wm.call_menu_pie", text="keFit2Grid", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid"
        pie.operator("wm.call_menu_pie", text="keFit2Grid Micro", icon="DOT").name = "VIEW3D_MT_ke_pie_fit2grid_micro"
        pie.operator("wm.call_menu_pie", text="keOrientPivot", icon="DOT").name = "VIEW3D_MT_ke_pie_orientpivot"
        pie.operator("wm.call_menu_pie", text="keOverlays", icon="DOT").name = "VIEW3D_MT_ke_pie_overlays"
        pie.operator("wm.call_menu_pie", text="keShading", icon="DOT").name = "VIEW3D_MT_ke_pie_shading"
        pie.operator("wm.call_menu_pie", text="keSnapAlign", icon="DOT").name = "VIEW3D_MT_ke_pie_align"
        pie.operator("wm.call_menu_pie", text="keFitPrim", icon="DOT").name = "VIEW3D_MT_ke_pie_fitprim"
        pie.operator("wm.call_menu_pie", text="keSubd", icon="DOT").name = "VIEW3D_MT_ke_pie_subd"


# Orientation & Pivot combo panels

class VIEW3D_PT_OPC(Panel):
    bl_label = "Orientation & Pivot Combos"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)


class VIEW3D_PT_OPC1(Panel):
    bl_label = "O&P Combo 1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_OPC"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('view3d.ke_opc', icon="ORIENTATION_GLOBAL", text="O&P Combo 1").combo="1"
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
        layout = self.layout
        col = layout.column(align=True)
        col.operator('view3d.ke_opc', icon="ORIENTATION_NORMAL", text="O&P Combo 2").combo="2"
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
        layout = self.layout
        col = layout.column(align=True)
        col.operator('view3d.ke_opc', icon="PIVOT_ACTIVE", text="O&P Combo 3").combo="3"
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
        layout = self.layout
        col = layout.column(align=True)
        col.operator('view3d.ke_opc', icon="ORIENTATION_CURSOR", text="O&P Combo 4").combo="4"
        col.label(text="OPC4 Object Mode")
        col.prop(context.scene.kekit, 'opc4_obj_o', text="Orient")
        col.prop(context.scene.kekit, 'opc4_obj_p', text="Pivot")
        col.label(text="OPC4 Edit Mode")
        col.prop(context.scene.kekit, 'opc4_edit_o', text="Orientation")
        col.prop(context.scene.kekit, 'opc4_edit_p', text="Pivot")


# -------------------------------------------------------------------------------------------------
# SUB TOOL PANELS (NOT SEPARATE PANEL MENU TABS)
# -------------------------------------------------------------------------------------------------



class VIEW3D_PT_Quick_Scale(Panel):
    bl_label = "Quick Scale"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene.kekit, "qs_user_value", text="Length:")
        col.separator()
        row = col.row()
        row.operator('VIEW3D_OT_ke_quickscale', text="X").user_axis = 0
        row.operator('VIEW3D_OT_ke_quickscale', text="Y").user_axis = 1
        row.operator('VIEW3D_OT_ke_quickscale', text="Z").user_axis = 2
        col = col.column()
        col.prop(context.scene.kekit, "qs_unit_size", text="Unit Size:")


class VIEW3D_PT_Mouse_Mirror(Panel):
    bl_label = "Mouse Mirror"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_mouse_mirror', icon="MOUSE_MOVE", text="MouseMirror").center = "BBOX"
        col.operator('VIEW3D_OT_ke_mouse_mirror', icon="MOUSE_MOVE", text="MouseMirror Active/World").center = "ACTIVE"
        col.operator('VIEW3D_OT_ke_mouse_mirror', icon="MOUSE_MOVE", text="MouseMirror Cursor").center = "CURSOR"
        col.separator()


class VIEW3D_PT_Mouse_Flip(Panel):
    bl_label = "Mouse Flip"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_parent_id = "VIEW3D_PT_kekit_modeling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_mouse_flip', icon="MOUSE_MOVE", text="MouseFlip").center = "MEDIAN"
        col.operator('VIEW3D_OT_ke_mouse_flip', icon="MOUSE_MOVE", text="MouseFlip Active").center = "ACTIVE"
        col.operator('VIEW3D_OT_ke_mouse_flip', icon="MOUSE_MOVE", text="MouseFlip Cursor").center = "CURSOR"
        col.separator()


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
        col.prop(context.scene.kekit, "unrotator_nosnap", text="Object Place Only (No snapping)")
        col.prop(context.scene.kekit, "unrotator_invert", text="Invert Rotation")
        col.prop(context.scene.kekit, "unrotator_center", text="Center on Face")


# -------------------------------------------------------------------------------------------------
# MENU
# -------------------------------------------------------------------------------------------------

class VIEW3D_PT_kekit(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'keKIT'
    bl_label = nfo
    # bl_options = {'HIDE_HEADER'}

    def draw_header_preset(self, context):
        layout = self.layout
        layout.emboss = 'NONE'
        row = layout.row(align=True)
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

        row = layout.row(align=True)
        row.operator('MESH_OT_ke_copyplus', text="Cut+").mode = "CUT"
        row.operator('MESH_OT_ke_copyplus', text="Copy+").mode = "COPY"
        row.operator('MESH_OT_ke_copyplus', text="Paste+").mode = "PASTE"
        col = layout.column(align=True)
        col.operator('VIEW3D_OT_ke_get_set_editmesh', icon="MOUSE_MOVE", text="Get & Set Edit Mode")
        col.operator('VIEW3D_OT_ke_get_set_material', icon="MOUSE_MOVE", text="Get & Set Material")
        row = layout.row(align=True)
        row.operator('VIEW3D_OT_ke_quickmeasure', text="Quick Measure").qm_start = "DEFAULT"
        row.operator('VIEW3D_OT_ke_quickmeasure', text="QM FreezeMode").qm_start = "SEL_SAVE"
        col.separator()

# -------------------------------------------------------------------------------------------------
# Prefs & Properties
# -------------------------------------------------------------------------------------------------

class ke_query_props(bpy.types.PropertyGroup):
    view_query: bpy.props.StringProperty(default=" N/A ")



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
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    ke_query_props,
    VIEW3D_PT_kekit,
    VIEW3D_PT_kekit_selection,
    VIEW3D_PT_kekit_modeling,
    VIEW3D_PT_Clean,
    VIEW3D_PT_Unrotator,
    VIEW3D_PT_FitPrim,
    VIEW3D_PT_Context_Tools,
    VIEW3D_PT_VPContextual,
    VIEW3D_PT_OPC,
    VIEW3D_PT_OPC1,
    VIEW3D_PT_OPC2,
    VIEW3D_PT_OPC3,
    VIEW3D_PT_OPC4,
    VIEW3D_PT_PieMenus,
    VIEW3D_PT_BlenderPieMenus,
    VIEW3D_PT_Mouse_Flip,
    VIEW3D_PT_Mouse_Mirror,
    VIEW3D_PT_Quick_Scale,
    VIEW3D_PT_ke_cursorbookmarks,
    VIEW3D_PT_ke_viewbookmarks
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
    ke_mouse_flip,
    ke_mouse_mirror,
    ke_quickmeasure,
    ke_fit2grid,
    ke_collision,
    ke_zeroscale,
    ke_quickscale,
    ke_clean,
    ke_lineararray,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.ke_query_props = bpy.props.PointerProperty(type=ke_query_props)

    for m in modules:
        m.register()

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
