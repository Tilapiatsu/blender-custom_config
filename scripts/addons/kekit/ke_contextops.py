bl_info = {
	"name": "keContextOps",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
}

import bpy
import bmesh
from bpy.types import Operator
from .ke_utils import get_loops
# from bpy.props import EnumProperty
# import rna_keymap_ui


class MESH_OT_ke_contextbevel(Operator):
	bl_idname = "mesh.ke_contextbevel"
	bl_label = "Context Bevel"
	bl_description = "VERTS selected: Vertex bevel Tool, EDGES: edge bevel, POLYS: Poly Inset"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.bevel('INVOKE_DEFAULT', vertex_only=True)
			elif sel_mode[1]:
				bpy.ops.mesh.bevel('INVOKE_DEFAULT', vertex_only=False)
			elif sel_mode[2]:
				bpy.ops.mesh.inset('INVOKE_DEFAULT', use_outset=False, )

		return {'FINISHED'}


class MESH_OT_ke_contextextrude(Operator):
	bl_idname = "mesh.ke_contextextrude"
	bl_label = "Context Extrude"
	bl_description = "VERTS selected: Vertex Extrude, EDGES: Edge Extrude, POLYS: Face extrude (Normal)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT')
			elif sel_mode[1]:
				bpy.ops.mesh.extrude_edges_move('INVOKE_DEFAULT')
			elif sel_mode[2]:
				bpy.ops.view3d.edit_mesh_extrude_move_normal('INVOKE_DEFAULT')

		return {'FINISHED'}


class VIEW3D_OT_ke_contextdelete(Operator):
	bl_idname = "view3d.ke_contextdelete"
	bl_label = "Context Delete"
	bl_description = "Deletes selection by selection mode (VERTEX, EDGE, POLY or OBJECT)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ctx_mode = bpy.context.mode
		if ctx_mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode
			if sel_mode[0]:
				bpy.ops.mesh.delete(type='VERT')
			elif sel_mode[1]:
				bpy.ops.mesh.delete(type='EDGE')
			elif sel_mode[2]:
				bpy.ops.mesh.delete(type='FACE')

		elif ctx_mode == "OBJECT":
			bpy.ops.object.delete()
			for item in bpy.context.selected_objects:
				bpy.data.objects.remove(item, do_unlink=True)

		return {'FINISHED'}


class MESH_OT_ke_contextdissolve(Operator):
	bl_idname = "mesh.ke_contextdissolve"
	bl_label = "Context Dissolve"
	bl_description = "Dissolves selection by selection mode (VERTEX, EDGE or POLY)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.dissolve_verts()
			elif sel_mode[1]:
				bpy.ops.mesh.dissolve_edges()
			elif sel_mode[2]:
				bpy.ops.mesh.dissolve_faces()

		return {'FINISHED'}


class VIEW3D_OT_ke_contextselect(Operator):
	bl_idname = "view3d.ke_contextselect"
	bl_label = "Context Select"
	bl_description = "EDGES: loop select, POLYS: Linked select, VERTS: (linked) Border edges" \
					 "Intended for Double-click LMB linked-select. (You have to assign dbl-click in preferences)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.mesh.region_to_loop()
				sel_verts = [v for v in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if v.select]
				if sel_verts:
					bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
				else:
					bpy.ops.mesh.select_all(action='DESELECT')
					fail_info = "ContextSelect(Vertex) Found no open borders - Nothing selected."
					self.report({'INFO'}, fail_info)

			elif sel_mode[1]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT')

			elif sel_mode[2]:
				bpy.ops.mesh.select_linked(delimit=set())

		return {'FINISHED'}


class VIEW3D_OT_ke_contextselect_extend(Operator):
	bl_idname = "view3d.ke_contextselect_extend"
	bl_label = "Context Select Extend"
	bl_description = "Extends Context Select. Intended for Shift-Double-click LMB" \
					 "(You have to assign dbl-click in preferences)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.mesh.region_to_loop()
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
			elif sel_mode[1]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT', extend=True)

			elif sel_mode[2]:
				bpy.ops.mesh.select_linked(delimit=set())

		return {'FINISHED'}


class VIEW3D_OT_ke_contextselect_subtract(Operator):
	bl_idname = "view3d.ke_contextselect_subtract"
	bl_label = "Context Select Subtract"
	bl_description = "Subtracts Context Select. Intended for Ctrl-Double-click LMB" \
					 "(You have to assign dbl-click in preferences)"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = bpy.context.tool_settings.mesh_select_mode

			if sel_mode[0]:
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.mesh.region_to_loop()
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
			elif sel_mode[1]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT', deselect=True)

			elif sel_mode[2]:
				bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT', deselect=True)

		return {'FINISHED'}


class VIEW3D_OT_ke_selmode(Operator):
	bl_idname = "view3d.ke_selmode"
	bl_label = "Direct Element <-> Object Mode Switch"
	bl_description = "Set Element Mode - Direct to selection mode from Object Mode"

	edit_mode: bpy.props.EnumProperty(
		items=[("VERT", "Vertex Edit Mode", "", "VERT", 1),
			   ("EDGE", "Edge Edit Mode", "", "EDGE", 2),
			   ("FACE", "Face Edit Mode", "", "FACE", 3),
			   ("OBJECT", "Object Mode", "", "OBJECT", 4)],
		name="Edit Mode",
		default="FACE")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sel_mode = bpy.context.mode
		obj = bpy.context.active_object
		if obj.type == 'MESH':
			em = self.edit_mode
			if em != 'OBJECT':
				if sel_mode == 'OBJECT':
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_mode(type=em)
				else:
					bpy.ops.mesh.select_mode(type=em)
			else:
				bpy.ops.object.editmode_toggle()
		return {'FINISHED'}


class MESH_OT_ke_bridge_or_fill(Operator):
	bl_idname = "mesh.ke_bridge_or_fill"
	bl_label = "Bridge or Fill"
	bl_description = "Bridge, except when ONE continous border edge-loop is selected: Grid Fill"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		obj = bpy.context.active_object
		mesh = obj.data
		bm = bmesh.from_edit_mesh(mesh)
		bm.edges.ensure_lookup_table()

		vert_pairs = []
		for e in bm.edges:
			if e.select:
				vp = [v for v in e.verts]
				vert_pairs.append(vp)

		if vert_pairs:
			check_loops = get_loops(vert_pairs, legacy=True)
			if len(check_loops) == 1 and check_loops[0][0] == check_loops[-1][-1]:
				try: bpy.ops.mesh.fill_grid('INVOKE_DEFAULT', True)
				except:
					try: bpy.ops.mesh.f2('INVOKE_DEFAULT')
					except: bpy.ops.mesh.fill('INVOKE_DEFAULT')
			else:
				bpy.ops.mesh.bridge_edge_loops('INVOKE_DEFAULT', True)

		return {'FINISHED'}


class MESH_OT_ke_maya_connect(Operator):
	bl_idname = "mesh.ke_maya_connect"
	bl_label = "Maya Connect"
	bl_description = "EDGE (or FACE) selection: Subdivide, VERTS: Connect Verts"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = [m for m in bpy.context.tool_settings.mesh_select_mode]
			if sel_mode[0]:
				bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
			elif sel_mode[1] or sel_mode[2]:
				bpy.ops.mesh.subdivide('INVOKE_DEFAULT')

		return {'FINISHED'}


class MESH_OT_ke_triple_connect_spin(Operator):
	bl_idname = "mesh.ke_triple_connect_spin"
	bl_label = "TripleConnectSpin"
	bl_description = "VERTS: Connect Verts, EDGE(s): Spin, FACE(s): Triangulate"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if bpy.context.mode == "EDIT_MESH":
			sel_mode = [m for m in bpy.context.tool_settings.mesh_select_mode]
			if sel_mode[0]:
				bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
			elif sel_mode[1]:
				bpy.ops.mesh.edge_rotate(use_ccw=False)
			elif sel_mode[2]:
				bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

		return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	MESH_OT_ke_contextbevel,
	MESH_OT_ke_contextextrude,
	MESH_OT_ke_contextdissolve,
	VIEW3D_OT_ke_contextdelete,
	VIEW3D_OT_ke_contextselect,
	VIEW3D_OT_ke_contextselect_extend,
	VIEW3D_OT_ke_contextselect_subtract,
	MESH_OT_ke_bridge_or_fill,
	MESH_OT_ke_maya_connect,
    MESH_OT_ke_triple_connect_spin,
	VIEW3D_OT_ke_selmode,
)


def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()
