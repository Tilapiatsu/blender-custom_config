bl_info = {
	"name": "kekit_misc",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 1, 0),
	"blender": (2, 80, 0),
}
import bpy
import bmesh

# -------------------------------------------------------------------------------------------------
# Selection
# -------------------------------------------------------------------------------------------------
class MESH_OT_ke_select_boundary(bpy.types.Operator):
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


class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
	bl_idname = "view3d.origin_to_selected"
	bl_label = "Origin To Selected Elements"
	bl_description = "Places origin(s) at element (or object(s)) selection (average)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			for area in bpy.context.screen.areas:
				if area.type == 'VIEW_3D':
					context = bpy.context.copy()
					context['area'] = area
					context['region'] = area.regions[-1]
					bpy.ops.view3d.snap_cursor_to_selected(context)
					bpy.ops.object.mode_set(mode="OBJECT")
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
					bpy.ops.view3d.snap_cursor_to_center()
					break
		return {'FINISHED'}


class VIEW3D_OT_ke_overlays(bpy.types.Operator):
	bl_idname = "view3d.ke_overlays"
	bl_label = "Overlay Options & Toggles"
	bl_description = "Overlay Options & Toggles"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER'}

	overlay: bpy.props.EnumProperty(
		items=[("WIRE", "Show Wireframe", "", "WIRE", 1),
			   ("EXTRAS", "Show Extras", "", "EXTRAS", 2)],
		name="Overlay Type",
		default="WIRE")

	def execute(self, context):
		if bpy.context.mode == "OBJECT":

			if self.overlay == "WIRE":
				status = bpy.context.space_data.overlay.show_wireframes
				bpy.context.space_data.overlay.show_wireframes = not status

			elif self.overlay == "EXTRAS":
				status = bpy.context.space_data.overlay.show_extras
				bpy.context.space_data.overlay.show_extras = not status

		elif bpy.context.mode == "EDIT_MESH":
			print("wip")
			# edge creasing variants
			# vertex normals
			# indices
		return {'FINISHED'}


class VIEW3D_OT_ke_frame_view(bpy.types.Operator):
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

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	MESH_OT_ke_select_boundary,
	VIEW3D_OT_origin_to_selected,
	VIEW3D_OT_ke_overlays,
	VIEW3D_OT_ke_frame_view,
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
