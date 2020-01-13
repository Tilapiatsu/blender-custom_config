bl_info = {
	"name": "kekit_misc",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 0, 0),
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
	bl_description = " Select Boundary ('region_to_loop') that also sets one edge to active. " \
					 "Also, in when "
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
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


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	MESH_OT_ke_select_boundary,
	VIEW3D_OT_origin_to_selected,
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
