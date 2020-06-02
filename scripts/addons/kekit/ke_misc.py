bl_info = {
	"name": "kekit_misc",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 3, 1),
	"blender": (2, 80, 0),
}
import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from .ke_utils import mouse_raycast
# -------------------------------------------------------------------------------------------------
# Selection
# -------------------------------------------------------------------------------------------------
class MESH_OT_ke_select_boundary(Operator):
	bl_idname = "mesh.ke_select_boundary"
	bl_label = "select boundary(+active)"
	bl_description = " Select Boundary ('region_to_loop') that also sets one edge to active. "
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		obj = bpy.context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		bpy.ops.mesh.region_to_loop()
		sel_edges = [e for e in bm.edges if e.select]
		if sel_edges:
			bm.select_history.clear()
			bm.select_history.add(sel_edges[0])
			bmesh.update_edit_mesh(obj.data, True)
		else:
			bpy.context.tool_settings.mesh_select_mode = (False, True, False)
		return {"FINISHED"}


class VIEW3D_OT_origin_to_selected(Operator):
	bl_idname = "view3d.origin_to_selected"
	bl_label = "Origin To Selected Elements"
	bl_description = "Places origin(s) at element selection average"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH')

	def execute(self, context):
		cursor = context.scene.cursor
		rot = list(cursor.rotation_quaternion)
		loc = list(cursor.location)

		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				context = bpy.context.copy()
				context['area'] = area
				context['region'] = area.regions[-1]

			if bpy.context.mode != "EDIT_MESH":
				bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
			else:
				# context.scene.objects
				# if len(context.ob)
				bpy.ops.view3d.snap_cursor_to_selected()
				bpy.ops.object.mode_set(mode="OBJECT")
				bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
				cursor.location = loc
				cursor.rotation_quaternion = rot
				break

		return {'FINISHED'}


class VIEW3D_OT_ke_object_to_cursor(Operator):
	bl_idname = "view3d.ke_object_to_cursor"
	bl_label = "Align Object To Cursor"
	bl_description = "Aligns selected object(s) to Cursor (Rotation & Location)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		cursor = context.scene.cursor
		for obj in context.selected_objects:
			obj.location = cursor.location
			og_rot_mode = str(obj.rotation_mode)
			obj.rotation_mode = "QUATERNION"
			obj.rotation_quaternion = cursor.rotation_quaternion
			obj.rotation_mode = og_rot_mode

		return {'FINISHED'}


class VIEW3D_OT_ke_origin_to_cursor(Operator):
	bl_idname = "view3d.ke_origin_to_cursor"
	bl_label = "Align Origin To Cursor"
	bl_description = "Aligns selected object(s) origin(s) (ONLY) to Cursor (Rotation & Location)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH')

	def execute(self, context):
		if context.object.data.is_editmode:
			bpy.ops.object.mode_set(mode="OBJECT")

		context.scene.tool_settings.use_transform_data_origin = True
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
		bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='CURSOR', mirror=True,
									use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
									proportional_size=1, use_proportional_connected=False,
									use_proportional_projected=False)
		context.scene.tool_settings.use_transform_data_origin = False

		return {'FINISHED'}


class VIEW3D_OT_ke_overlays(Operator):
	bl_idname = "view3d.ke_overlays"
	bl_label = "Overlay Options & Toggles"
	bl_description = "Overlay Options & Toggles"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	overlay: bpy.props.EnumProperty(
		items=[("WIRE", "Show Wireframe", "", "WIRE", 1),
			   ("EXTRAS", "Show Extras", "", "EXTRAS", 2),
			   ("SEAMS", "Show Edge Seams", "", "SEAMS", 3),
			   ("SHARP", "Show Edge Sharp", "", "SHARP", 4),
			   ("CREASE", "Show Edge Crease", "", "CREASE", 5),
			   ("BEVEL", "Show Edge Bevel Weight", "", "BEVEL", 6),
			   ("FACEORIENT", "Show Face Orientation", "", "FACEORIENT", 7),
			   ("INDICES", "Show Indices", "", "INDICES", 8),
			   ("ALLEDIT", "Toggle Edit Overlays", "", "ALLEDIT", 9),
			   ("ALL", "Toggle Overlays", "", "ALL", 10),
			   ("VN", "Vertex Normals", "", "VN", 11),
			   ("SN", "Split Normals", "", "SN", 12),
			   ("FN", "Face Normals", "", "FN", 13),
			   ("BACKFACE", "Backface Culling", "", "BACKFACE", 14),
			   ("ORIGINS", "Show Origins", "", "ORIGINS", 15),
			   ("CURSOR", "Show Cursor", "", "CURSOR", 16),
			   ("OUTLINE", "Show Outline", "", "OUTLINE", 17),
			   ],
		name="Overlay Type",
		default="WIRE")

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":

			if self.overlay == "EXTRAS":
				status = bpy.context.space_data.overlay.show_extras
				bpy.context.space_data.overlay.show_extras = not status

			elif self.overlay == "SEAMS":
				status = bpy.context.space_data.overlay.show_edge_seams
				bpy.context.space_data.overlay.show_edge_seams = not status

			elif self.overlay == "SHARP":
				status = bpy.context.space_data.overlay.show_edge_sharp
				bpy.context.space_data.overlay.show_edge_sharp = not status

			elif self.overlay == "CREASE":
				status = bpy.context.space_data.overlay.show_edge_crease
				bpy.context.space_data.overlay.show_edge_crease = not status

			elif self.overlay == "BEVEL":
				status = bpy.context.space_data.overlay.show_edge_bevel_weight
				bpy.context.space_data.overlay.show_edge_bevel_weight = not status

			elif self.overlay == "FACEORIENT":
				status = bpy.context.space_data.overlay.show_face_orientation
				bpy.context.space_data.overlay.show_face_orientation = not status

			elif self.overlay == "INDICES":
				status = bpy.context.space_data.overlay.show_extra_indices
				bpy.context.space_data.overlay.show_extra_indices = not status

			elif self.overlay == "ALLEDIT":
				if bpy.context.space_data.overlay.show_edge_seams or bpy.context.space_data.overlay.show_edge_sharp:
					bpy.context.space_data.overlay.show_edge_seams = False
					bpy.context.space_data.overlay.show_edge_sharp = False
					bpy.context.space_data.overlay.show_edge_crease = False
					bpy.context.space_data.overlay.show_edge_bevel_weight = False
				else:
					bpy.context.space_data.overlay.show_edge_seams = True
					bpy.context.space_data.overlay.show_edge_sharp = True
					bpy.context.space_data.overlay.show_edge_crease = True
					bpy.context.space_data.overlay.show_edge_bevel_weight = True

			elif self.overlay == "ALL":
				status = bpy.context.space_data.overlay.show_overlays
				bpy.context.space_data.overlay.show_overlays = not status

			elif self.overlay == "VN":
				status = bpy.context.space_data.overlay.show_vertex_normals
				bpy.context.space_data.overlay.show_vertex_normals = not status

			elif self.overlay == "SN":
				status = bpy.context.space_data.overlay.show_split_normals
				bpy.context.space_data.overlay.show_split_normals = not status

			elif self.overlay == "FN":
				status = bpy.context.space_data.overlay.show_face_normals
				bpy.context.space_data.overlay.show_face_normals = not status

			elif self.overlay == "BACKFACE":
				status = bpy.context.space_data.shading.show_backface_culling
				bpy.context.space_data.shading.show_backface_culling = not status

			elif self.overlay == "ORIGINS":
				status = bpy.context.space_data.overlay.show_object_origins
				bpy.context.space_data.overlay.show_object_origins = not status

			elif self.overlay == "OUTLINE":
				status = bpy.context.space_data.overlay.show_outline_selected
				bpy.context.space_data.overlay.show_outline_selected = not status

			elif self.overlay == "CURSOR":
				status = bpy.context.space_data.overlay.show_cursor
				bpy.context.space_data.overlay.show_cursor = not status


		elif bpy.context.mode == "OBJECT":

			if self.overlay == "WIRE":
				status = bpy.context.space_data.overlay.show_wireframes
				bpy.context.space_data.overlay.show_wireframes = not status

			elif self.overlay == "EXTRAS":
				status = bpy.context.space_data.overlay.show_extras
				bpy.context.space_data.overlay.show_extras = not status

			elif self.overlay == "ALL":
				status = bpy.context.space_data.overlay.show_overlays
				bpy.context.space_data.overlay.show_overlays = not status

			elif self.overlay == "ORIGINS":
				status = bpy.context.space_data.overlay.show_object_origins
				bpy.context.space_data.overlay.show_object_origins = not status

			elif self.overlay == "OUTLINE":
				status = bpy.context.space_data.overlay.show_outline_selected
				bpy.context.space_data.overlay.show_outline_selected = not status

			elif self.overlay == "CURSOR":
				status = bpy.context.space_data.overlay.show_cursor
				bpy.context.space_data.overlay.show_cursor = not status

		return {'FINISHED'}


class VIEW3D_OT_ke_frame_view(Operator):
	bl_idname = "view3d.ke_frame_view"
	bl_label = "Frame All or Selected in View"
	bl_description = "Frame Selection in View, or everything if nothing is selected."
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	def execute(self, context):
		sel_mode = bpy.context.mode
		sel_obj = [o for o in bpy.context.scene.objects if o.select_get()]

		if sel_mode == "OBJECT":
			if sel_obj:
				bpy.ops.view3d.view_selected('INVOKE_DEFAULT', use_all_regions=False)
			else:
				bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=True)

		elif sel_mode == "EDIT_MESH":

			bpy.ops.object.mode_set(mode="OBJECT")
			sel_check = False

			for o in bpy.context.scene.objects:
				if not sel_check and o.type == "MESH":
					for v in o.data.vertices:
						if v.select:
							sel_check = True
							break

			bpy.ops.object.mode_set(mode="EDIT")

			if sel_check:
				bpy.ops.view3d.view_selected('INVOKE_DEFAULT', use_all_regions=False)

			else:
				bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=True)

		return {'FINISHED'}


class VIEW3D_OT_ke_spacetoggle(Operator):
	bl_idname = "view3d.ke_spacetoggle"
	bl_label = "Space Toggle"
	bl_description = "Toggle between Edit Mesh and Object modes when mouse pointer is over -nothing-."
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	mouse_pos = Vector((0, 0))

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH')

	def invoke(self, context, event):
		self.mouse_pos[0] = event.mouse_region_x
		self.mouse_pos[1] = event.mouse_region_y
		return self.execute(context)

	def execute(self, context):
		sel_mode = bpy.context.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		obj, hit_wloc, hit_normal, face_index = mouse_raycast(context, self.mouse_pos)

		if not face_index:
			if sel_mode == "OBJECT":
				bpy.ops.object.mode_set(mode="EDIT")
			elif sel_mode == "EDIT_MESH":
				bpy.ops.object.mode_set(mode="OBJECT")

		return {'FINISHED'}


def get_og_overlay_ui(self):
	og_gizmo = bpy.context.space_data.show_gizmo_navigate
	og_floor = bpy.context.space_data.overlay.show_floor
	og_x = bpy.context.space_data.overlay.show_axis_x
	og_y = bpy.context.space_data.overlay.show_axis_y
	og_z = bpy.context.space_data.overlay.show_axis_z
	og_text = bpy.context.space_data.overlay.show_text
	og_extras = bpy.context.space_data.overlay.show_extras

	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					og_ui = space.show_region_ui
					og_tb = space.show_region_toolbar

	return [og_gizmo, og_floor, og_x, og_y, og_z, og_text, og_extras, og_ui, og_tb]


class VIEW3D_OT_ke_focusmode(Operator):
	bl_idname = "view3d.ke_focusmode"
	bl_label = "Focus Mode"
	bl_description = "Fullscreen+. Restores original settings when toggled back."
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	supermode : bpy.props.BoolProperty(default=False)

	def execute(self, context):

		set_focus = bpy.context.scene.ke_focus[0]
		set_super_focus = bpy.context.scene.ke_focus[10]

		if not set_focus:
			og = get_og_overlay_ui(self)

			context.space_data.show_gizmo_navigate = False
			context.space_data.overlay.show_floor = False
			context.space_data.overlay.show_axis_x = False
			context.space_data.overlay.show_axis_y = False
			context.space_data.overlay.show_axis_z = False
			context.space_data.overlay.show_text = False
			context.space_data.overlay.show_extras = False

			context.scene.ke_focus[1] = og[0]
			context.scene.ke_focus[2] = og[1]
			context.scene.ke_focus[3] = og[2]
			context.scene.ke_focus[4] = og[3]
			context.scene.ke_focus[5] = og[4]
			context.scene.ke_focus[6] = og[5]
			context.scene.ke_focus[7] = og[6]
			context.scene.ke_focus[8] = og[7]
			context.scene.ke_focus[9] = og[8]

			context.scene.ke_focus[0] = True
			if self.supermode: context.scene.ke_focus[10] = True

			bpy.ops.screen.screen_full_area(use_hide_panels=self.supermode)

			for area in context.screen.areas:
				if area.type == 'VIEW_3D':
					for space in area.spaces:
						if space.type == 'VIEW_3D':
							space.show_region_ui = False
							space.show_region_toolbar = False

		else:
			og = bpy.context.scene.ke_focus[1:]

			context.space_data.show_gizmo_navigate = og[0]
			context.space_data.overlay.show_floor = og[1]
			context.space_data.overlay.show_axis_x = og[2]
			context.space_data.overlay.show_axis_y = og[3]
			context.space_data.overlay.show_axis_z = og[4]
			context.space_data.overlay.show_text = og[5]
			context.space_data.overlay.show_extras = og[6]

			context.scene.ke_focus[0] = False
			context.scene.ke_focus[10] = False

			if not self.supermode and set_super_focus:
				bpy.ops.screen.screen_full_area(use_hide_panels=True)
			elif self.supermode and not set_super_focus:
				bpy.ops.screen.screen_full_area(use_hide_panels=False)
			else:
				bpy.ops.screen.screen_full_area(use_hide_panels=self.supermode)

			for area in context.screen.areas:
				if area.type == 'VIEW_3D':
					for space in area.spaces:
						if space.type == 'VIEW_3D':
							space.show_region_ui = og[7]
							space.show_region_toolbar = og[8]

		return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	MESH_OT_ke_select_boundary,
	VIEW3D_OT_origin_to_selected,
	VIEW3D_OT_ke_overlays,
	VIEW3D_OT_ke_frame_view,
	VIEW3D_OT_ke_spacetoggle,
	VIEW3D_OT_ke_focusmode,
	VIEW3D_OT_ke_object_to_cursor,
	VIEW3D_OT_ke_origin_to_cursor,
)

def register():
	for c in classes:
		bpy.utils.register_class(c)
	bpy.types.Scene.ke_focus = bpy.props.BoolVectorProperty(size=16)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)
	try:
		del bpy.types.Scene.ke_focus
	except Exception as e:
		print('unregister fail:\n', e)
		pass

if __name__ == "__main__":
	register()
