bl_info = {
	"name": "keKIT",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 2, 2),
	"blender": (2, 80, 0),
	"location": "View3D > Sidebar",
	"warning": "",
	"description": "Modeling scripts etc",
	"wiki_url": "http://artbykjell.com",
	"category": "Mesh",
}
# -------------------------------------------------------------------------------------------------
# Note: This kit is very much WIP - ..and partially experimental.
# -------------------------------------------------------------------------------------------------

from . import ke_orient_and_pivot
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

# from .box_primitive import MESH_OT_primitve_box_add

import bpy

from bpy.types import (
		Menu,
		Panel,
		PropertyGroup,
		AddonPreferences,
		)
from bpy.props import (
		BoolProperty,
		PointerProperty,
		StringProperty,
		IntProperty,
		FloatProperty,
		)


# -------------------------------------------------------------------------------------------------
# SUB MENU PANELS
# -------------------------------------------------------------------------------------------------

class VIEW3D_PT_Orient_and_Pivot(Panel):
	bl_label = "Orientation & Pivot Combo"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'keKIT'
	bl_parent_id = "VIEW3D_PT_kekit"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.operator('view3d.orient_and_pivot_global', icon="ORIENTATION_GLOBAL", text="Orient & Pivot (Global)")
		col.operator('view3d.orient_and_pivot_local', icon="ORIENTATION_NORMAL", text="Orient & Pivot (Local)")
		col.operator('view3d.orient_and_pivot_local_active', icon="PIVOT_ACTIVE", text="Orient & Pivot (Local Active)")
		col.operator('view3d.orient_and_pivot_cursor', icon="ORIENTATION_CURSOR", text="Orient & Pivot (Cursor)")
		col.separator()


class VIEW3D_PT_Context_Tools(Panel):
	bl_label = "Context Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'keKIT'
	bl_parent_id = "VIEW3D_PT_kekit"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.operator('MESH_OT_ke_contextbevel', text="Context Bevel")
		col.operator('MESH_OT_ke_contextextrude', text="Context Extrude")
		col.operator('VIEW3D_OT_ke_contextdelete', text="Context Delete")
		col.operator('MESH_OT_ke_contextdissolve', text="Context Dissolve")
		col.operator('VIEW3D_OT_ke_contextselect', text="Context Select")
		col.operator('VIEW3D_OT_ke_contextselect_extend', text="Context Select Extend")
		col.operator('VIEW3D_OT_ke_contextselect_subtract', text="Context Select Subtract")
		col.operator('MESH_OT_ke_bridge_or_fill', text="Bridge or Fill")
		col.operator('MESH_OT_ke_maya_connect', text="Maya Connect")
		col.operator('MESH_OT_ke_triple_connect_spin', text="Triple Connect Spin")
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
		col.operator('MESH_OT_ke_fitprim', text="FitPrim Cube", icon="MESH_CUBE").ke_fitprim_option = "BOX"
		col.operator('MESH_OT_ke_fitprim', text="FitPrim Cylinder", icon="MESH_CYLINDER").ke_fitprim_option = "CYL"
		col.separator()
		col.label(text="Options")
		col.prop(context.scene.kekit, "fitprim_sides", text="Cylinder Default Sides:")
		col.prop(context.scene.kekit, "fitprim_modal", text="Modal Cylinder")
		col.prop(context.scene.kekit, "fitprim_unit", text="No-sel Unit Size")
		col.prop(context.scene.kekit, "fitprim_select", text="Select Result")


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
		pie.operator("wm.call_menu_pie", text="Proportional Editing Falloff", icon="DOT").name = \
			"VIEW3D_MT_proportional_editing_falloff_pie"
		pie.operator("wm.call_menu_pie", text="View Pie", icon="DOT").name = \
			"VIEW3D_MT_view_pie"
		pie.operator("wm.call_menu_pie", text="Pivot Pie", icon="DOT").name = \
			"VIEW3D_MT_pivot_pie"
		pie.operator("wm.call_menu_pie", text="Orientation Pie", icon="DOT").name = \
			"VIEW3D_MT_orientations_pie"
		pie.operator("wm.call_menu_pie", text="Shading Pie", icon="DOT").name = \
			"VIEW3D_MT_shading_pie"
		pie.operator("wm.call_menu_pie", text="Snap Pie", icon="DOT").name = \
			"VIEW3D_MT_snap_pie"
		pie.operator("wm.call_menu_pie", text="UV: Snap Pie", icon="DOT").name = \
			"IMAGE_MT_uvs_snap_pie"
		pie.separator()
		pie.operator("wm.call_menu_pie", text="Clip: Tracking", icon="DOT").name = \
			"CLIP_MT_tracking_pie"
		pie.operator("wm.call_menu_pie", text="Clip: Solving", icon="DOT").name = \
			"CLIP_MT_solving_pie"
		pie.operator("wm.call_menu_pie", text="Clip: Marker", icon="DOT").name = \
			"CLIP_MT_marker_pie"
		pie.operator("wm.call_menu_pie", text="Clip: Reconstruction", icon="DOT").name = \
			"CLIP_MT_reconstruction_pie"


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
	bl_label = "keKIT v1.22"
	# bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		# kwm = context.window_manager.kekit
		layout = self.layout
		col = layout.column(align=True)
		# col.operator('wm.url_open', text="Help (web)").url="artbykjell.com"  # IE11 ?!
		# col.label(text="General")
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
		row.operator('MESH_OT_ke_itemize', text="Itemize")
		row.operator('MESH_OT_ke_itemize', text="Itemize (Copy)").ke_itemize_dupe = True
		col = layout.column(align=True)
		col.operator('MESH_OT_ke_unbevel', text="Unbevel")


# -------------------------------------------------------------------------------------------------
# Prefs & Properties
# -------------------------------------------------------------------------------------------------

panels = (
		VIEW3D_PT_kekit,
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


# WIP props ---------------------------------------------------------------------------------------

class kekit_properties(PropertyGroup):
	fitprim_select : BoolProperty(
		default=False)
	fitprim_modal : BoolProperty(
		default=True)
	fitprim_sides : IntProperty(
		min=3, max=256,
		default=16)
	fitprim_unit : FloatProperty(
		min=.00001, max=256,
		default=.2)
	unrotator_reset : BoolProperty(
		default=True)
	unrotator_connect : BoolProperty(
		default=True)
	unrotator_nolink : BoolProperty(
		default=False)


class keKITprefs(AddonPreferences):
	# this must match the addon name, use '__package__'
	# when defining this in a submodule of a python package.
	bl_idname = __name__

	category: StringProperty(
			name="Tab Category",
			description="The name for the category of the panel",
			default="keKIT",
			update=update_panel
			)

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		col = row.column()
		col.label(text="Tab Category:")
		col.prop(self, "category", text="")


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	VIEW3D_PT_kekit,
	VIEW3D_PT_Unrotator,
	VIEW3D_PT_FitPrim,
	VIEW3D_PT_Orient_and_Pivot,
	VIEW3D_PT_Context_Tools,
	kekit_properties,
	keKITprefs,
	VIEW3D_PT_PieMenus,
	VIEW3D_PT_BlenderPieMenus,
	)

modules = (
	ke_orient_and_pivot,
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
)


def register():

	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.kekit = PointerProperty(type=kekit_properties)

	for m in modules:
		m.register()


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	try:
		del bpy.types.Scene.kekit
	except Exception as e:
		print('unregister fail:\n', e)
		pass

	for m in modules:
		m.unregister()


if __name__ == "__main__":
	register()
