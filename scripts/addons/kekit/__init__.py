bl_info = {
	"name": "keKIT",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 2, 7),
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
from ._prefs import get_prefs, write_prefs, VIEW3D_OT_ke_prefs_save

from . import ke_orient_and_pivot
from . import ke_cursor_fit
from . import ke_copypasteplus
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

import bpy
from bpy.types import Panel

nfo = "keKit v1.271"

# -------------------------------------------------------------------------------------------------
# SUB MENU PANELS
# -------------------------------------------------------------------------------------------------

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
		# bpy.ops.mesh.dissolve_mode('INVOKE_DEFAULT')
		col.operator('MESH_OT_dissolve_mode', text="Context Dissolve (Blender)")
		col.operator('MESH_OT_ke_contextdissolve', text="Context Dissolve")
		col.operator('VIEW3D_OT_ke_contextselect', text="Context Select")
		col.operator('VIEW3D_OT_ke_contextselect_extend', text="Context Select Extend")
		col.operator('VIEW3D_OT_ke_contextselect_subtract', text="Context Select Subtract")
		col.operator('MESH_OT_ke_bridge_or_fill', text="Bridge or Fill")
		col.operator('MESH_OT_ke_maya_connect', text="Maya Connect")
		col.operator('MESH_OT_ke_triple_connect_spin', text="Triple Connect Spin")
		col.operator("VIEW3D_OT_ke_frame_view", text="Frame All or Selected")
		col.separator()


class VIEW3D_PT_FitPrim(Panel):
	bl_label = "FitPrim"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'keKIT'
	bl_parent_id = "VIEW3D_PT_kekit"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cube", icon="MESH_CUBE").ke_fitprim_option = "BOX"
		col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Cylinder", icon="MESH_CYLINDER").ke_fitprim_option = "CYL"
		col.operator('VIEW3D_OT_ke_fitprim', text="FitPrim Sphere", icon="MESH_UVSPHERE").ke_fitprim_option = "SPHERE"
		col.separator()
		col.label(text="Options")
		col.prop(context.scene.kekit, "fitprim_unit", text="No-sel Unit Size")
		col.separator()
		col.prop(context.scene.kekit, "fitprim_sides", text="Cylinder Default Sides:")
		col.prop(context.scene.kekit, "fitprim_modal", text="Modal Cylinder")
		col.prop(context.scene.kekit, "fitprim_sphere_seg", text="Sphere Segments")
		col.prop(context.scene.kekit, "fitprim_sphere_ring", text="Sphere Rings")
		col.prop(context.scene.kekit, "fitprim_select", text="Select Result")
		col.prop(context.scene.kekit, "fitprim_item", text="Make Object")


class VIEW3D_PT_Unrotator(Panel):
	bl_label = "Unrotator"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'keKIT'
	bl_parent_id = "VIEW3D_PT_kekit"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator", icon="ORIENTATION_NORMAL").ke_unrotator_option = "DEFAULT"
		col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator Duplicate", icon="LINKED").ke_unrotator_option = "DUPE"
		col.operator('VIEW3D_OT_ke_unrotator', text="Unrotator RotOnly", icon="ORIENTATION_LOCAL").ke_unrotator_option = "NO_LOC"
		col.separator()
		col.label(text="Options")
		col.prop(context.scene.kekit, "unrotator_reset", text="Auto-Reset")
		col.prop(context.scene.kekit, "unrotator_connect", text="Auto-Select Linked")
		col.prop(context.scene.kekit, "unrotator_nolink", text="Object Duplicate Unlinked")


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


# -------------------------------------------------------------------------------------------------
# MENU
# -------------------------------------------------------------------------------------------------

class VIEW3D_PT_kekit(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'keKIT'
	bl_label = nfo
	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		# kwm = context.window_manager.kekit
		layout = self.layout
		col = layout.column(align=True)
		# col.operator('wm.url_open', text="Help (web)").url="artbykjell.com"  # IE11 ?!
		# col.label(text="General")
		col.operator('VIEW3D_OT_ke_prefs_save', text="Save Kit Settings")
		col.separator()
		row = layout.row(align=True)
		row.operator('VIEW3D_OT_ke_selmode', text="Vert").edit_mode = "VERT"
		row.operator('VIEW3D_OT_ke_selmode', text="Edge").edit_mode = "EDGE"
		row.operator('VIEW3D_OT_ke_selmode', text="Face").edit_mode = "FACE"
		row.operator('VIEW3D_OT_ke_selmode', text="Object").edit_mode = "OBJECT"
		row = layout.row(align=True)
		row.operator('MESH_OT_copyplus', text="Copy+")
		row.operator('MESH_OT_pasteplus', text="Paste+")
		col = layout.column(align=True)
		col.operator("VIEW3D_OT_cursor_fit_selected_and_orient", text="Cursor Fit & Align")
		col.operator("MESH_OT_ke_select_boundary", text="Select Boundary (+Active)")
		col.operator('VIEW3D_OT_ke_get_set_editmesh', icon="MOUSE_MOVE", text="Get & Set Edit Mode")
		col.operator('VIEW3D_OT_ke_get_set_material', icon="MOUSE_MOVE", text="Get & Set Material")

		col = layout.column(align=True)
		col.separator()
		# col.label(text="Modeling")
		col.operator('MESH_OT_primitive_box_add', text="Add Box Primitive", icon = 'MESH_CUBE')
		col.operator('VIEW3D_OT_origin_to_selected', text="Object Origin(s) to Selection")
		col.operator('MESH_OT_merge_to_mouse',icon="MOUSE_MOVE", text="Merge To Mouse")
		col.operator('MESH_OT_ke_ground', text="Ground (or Center)")
		row = layout.row(align=True)
		row.operator('MESH_OT_ke_itemize', text="Itemize").mode = "DEFAULT"
		row.operator('MESH_OT_ke_itemize', text="Itemize-Copy").mode = "DUPE"
		col.separator()
		col.operator('MESH_OT_ke_unbevel', text="Unbevel")
		col = layout.column(align=True)
		col.operator('MESH_OT_ke_direct_loop_cut', text="Direct Loop Cut").mode = "DEFAULT"
		col.operator('MESH_OT_ke_direct_loop_cut', text="Direct Loop Cut & Slide").mode = "SLIDE"
		col = layout.column(align=True)
		col.operator('VIEW3D_OT_ke_overlays', text="Object Wireframe Toggle").overlay = "WIRE"
		col.operator('VIEW3D_OT_ke_overlays', text="Extras Toggle").overlay = "EXTRAS"


# -------------------------------------------------------------------------------------------------
# Prefs & Properties
# -------------------------------------------------------------------------------------------------

panels = (
		VIEW3D_PT_kekit,
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
	VIEW3D_PT_kekit,
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
	)

modules = (
	_prefs,
	ke_orient_and_pivot,
	ke_cursor_fit,
	ke_copypasteplus,
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
)


def register():

	for cls in classes:
		bpy.utils.register_class(cls)

	for m in modules:
		m.register()

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	for m in modules:
		m.unregister()


if __name__ == "__main__":
	register()
