bl_info = {
	"name": "keContextOps",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 4, 0),
	"blender": (2, 80, 0),
}

import bpy
import bmesh
from mathutils import Vector
from math import sqrt
from bpy.types import Operator
from .ke_utils import get_loops, mouse_raycast, get_selected, average_vector, get_duplicates
from bpy_extras.view3d_utils import region_2d_to_location_3d, location_3d_to_region_2d

# from bpy.props import EnumProperty
# import rna_keymap_ui


class MESH_OT_ke_contextslide(Operator):
	bl_idname = "mesh.ke_contextslide"
	bl_label = "Context Slide"
	bl_description = "Alternative one-click for double-G slide."

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		sel_mode = bpy.context.tool_settings.mesh_select_mode
		if sel_mode[0]:
			bpy.ops.transform.vert_slide("INVOKE_DEFAULT")
		else:
			bpy.ops.transform.edge_slide("INVOKE_DEFAULT")

		return {'FINISHED'}


class MESH_OT_ke_contextbevel(Operator):
	bl_idname = "mesh.ke_contextbevel"
	bl_label = "Context Bevel"
	bl_description = "VERTS selected: Vertex bevel Tool, EDGES: edge bevel, POLYS: Poly Inset"

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
		if sel_mode[0]:
			bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')
		elif sel_mode[1]:
			if context.scene.kekit.korean:
				bpy.ops.mesh.bevel('INVOKE_DEFAULT', segments=2, profile=1, affect='EDGES')
			else:
				bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='EDGES')
		elif sel_mode[2]:
			bpy.ops.mesh.inset('INVOKE_DEFAULT', use_outset=False)

		return {'FINISHED'}


class MESH_OT_ke_contextextrude(Operator):
	bl_idname = "mesh.ke_contextextrude"
	bl_label = "Context Extrude"
	bl_description = "VERTS selected: Vertex Extrude, EDGES: Edge Extrude, POLYS: Face Extrude Normal (Region)"

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		use_tt = context.scene.kekit.tt_extrude
		sel_mode = context.tool_settings.mesh_select_mode[:]

		if sel_mode[0]:
			if use_tt:
				am = bool(context.scene.tool_settings.use_mesh_automerge)
				if am:
					context.scene.tool_settings.use_mesh_automerge = False
				bpy.ops.mesh.extrude_vertices_move(MESH_OT_extrude_verts_indiv=None, TRANSFORM_OT_translate=None)
				if am:
					context.scene.tool_settings.use_mesh_automerge = True
				bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', mode="MOVE")
			else:
				bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT')

		elif sel_mode[1]:
			if use_tt:
				am = bool(context.scene.tool_settings.use_mesh_automerge)
				if am:
					context.scene.tool_settings.use_mesh_automerge = False
				bpy.ops.mesh.extrude_edges_move(MESH_OT_extrude_edges_indiv=None, TRANSFORM_OT_translate=None)
				if am:
					context.scene.tool_settings.use_mesh_automerge = True
				bpy.ops.view3d.ke_tt('INVOKE_DEFAULT', mode="MOVE")
			else:
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
				# bpy.ops.mesh.dissolve_edges(use_verts=True)
				bpy.ops.mesh.delete(type='EDGE')
			elif sel_mode[2]:
				bpy.ops.mesh.delete(type='FACE')

		elif ctx_mode == "OBJECT":
			sel = context.selected_objects[:]
			if context.scene.kekit.h_delete:
				bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE', extend=True)
				sel = context.selected_objects[:]

			for item in sel:
				bpy.data.objects.remove(item, do_unlink=True)

		return {'FINISHED'}


class MESH_OT_ke_contextdissolve(Operator):
	bl_idname = "mesh.ke_contextdissolve"
	bl_label = "Context Dissolve"
	bl_description = "Dissolves selection by selection mode (VERTEX, EDGE or POLY)"

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		# bpy.ops.mesh.dissolve_mode('INVOKE_DEFAULT')
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
		if sel_mode[0]:
			bpy.ops.mesh.dissolve_verts()
		elif sel_mode[1]:
			bpy.ops.mesh.dissolve_edges(use_verts=True)
			# bpy.ops.mesh.dissolve_limited()
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
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				og = [v for v in bm.verts if v.select]
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.mesh.region_to_loop()
				bpy.ops.ed.undo_push()
				sel_verts = [v for v in bm.verts if v.select]
				if sel_verts:
					bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
				else:
					bpy.context.tool_settings.mesh_select_mode = (True,False,False)
					for v in og:
						v.select = True
					bpy.ops.mesh.select_linked(delimit=set())
					bpy.ops.ed.undo_push()

			elif sel_mode[1]:
				bpy.ops.mesh.loop_multi_select(True, ring=False)
				bpy.ops.ed.undo_push()

			elif sel_mode[2]:
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.ed.undo_push()


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
				bpy.ops.ed.undo_push()

			elif sel_mode[1]:
				bpy.ops.mesh.loop_multi_select(ring=False)
				bpy.ops.ed.undo_push()

			elif sel_mode[2]:
				bpy.ops.mesh.select_linked(delimit=set())
				bpy.ops.ed.undo_push()

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
				bpy.ops.ed.undo_push()

			elif sel_mode[1]:
				bpy.ops.mesh.loop_select('INVOKE_DEFAULT', deselect=True)
				bpy.ops.ed.undo_push()
			elif sel_mode[2]:
				bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT', deselect=True)
				bpy.ops.ed.undo_push()
		return {'FINISHED'}


class VIEW3D_OT_ke_selmode(Operator):
	bl_idname = "view3d.ke_selmode"
	bl_label = "Direct Element <-> Object Mode Switch"
	bl_description = "Set Element Mode - Direct to selection mode from Object Mode"

	edit_mode: bpy.props.EnumProperty(
		items=[("VERT", "Vertex Edit Mode", "", 1),
			   ("EDGE", "Edge Edit Mode", "", 2),
			   ("FACE", "Face Edit Mode", "", 3),
			   ("OBJECT", "Object Mode", "", 4)],
		name="Edit Mode",
		default="OBJECT")

	mouse_pos = [0, 0]

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def invoke(self, context, event):
		self.mouse_pos[0] = event.mouse_region_x
		self.mouse_pos[1] = event.mouse_region_y
		return self.execute(context)

	def execute(self, context):
		mode = str(context.mode)
		has_componentmodes = {"MESH", "ARMATURE", "GPENCIL"}
		has_editmode_only = {"CURVE", "SURFACE", "LATTICE", "META", "HAIR", "FONT"}

		# Mouse Over select option
		if context.scene.kekit.selmode_mouse and context.space_data.type == "VIEW_3D":
			og_obj = context.object

			if mode != "OBJECT":
				bpy.ops.object.mode_set(mode="OBJECT")

			bpy.ops.view3d.select(extend=False, deselect=False, toggle=False, deselect_all=False, center=False,
								  enumerate=False, object=False, location=self.mouse_pos)

			sel_obj = context.object

			if og_obj == sel_obj:
				if mode == "OBJECT" and sel_obj.type in (has_componentmodes | has_editmode_only):
					bpy.ops.object.editmode_toggle()
				return {"FINISHED"}

			if mode != "OBJECT" and sel_obj.type in (has_componentmodes | has_editmode_only):
				bpy.ops.object.editmode_toggle()
			else:
				mode = "OBJECT"

		# Set selection mode
		if context.active_object is not None:
			obj = context.active_object
		else:
			obj = context.object

		if obj.type in has_componentmodes:

			if self.edit_mode != "OBJECT":

				if obj.type == "ARMATURE":
					bpy.ops.object.posemode_toggle()

				elif obj.type == "GPENCIL":
					if mode == "OBJECT":
						bpy.ops.gpencil.editmode_toggle()
					if self.edit_mode == "VERT":
						context.scene.tool_settings.gpencil_selectmode_edit = 'POINT'
					elif self.edit_mode == "EDGE":
						context.scene.tool_settings.gpencil_selectmode_edit = 'STROKE'
					elif self.edit_mode == "FACE":
						obj.data.use_curve_edit = not obj.data.use_curve_edit
				else:
					if mode == "OBJECT":
						bpy.ops.object.editmode_toggle()
					bpy.ops.mesh.select_mode(type=self.edit_mode)
			else:
				if obj.type == "GPENCIL":
					bpy.ops.gpencil.editmode_toggle()
				else:
					bpy.ops.object.editmode_toggle()

		elif obj.type in has_editmode_only:
			bpy.ops.object.editmode_toggle()

		else:
			# print("Object does not have an Edit Mode")
			return {"CANCELLED"}

		return {"FINISHED"}


class MESH_OT_ke_bridge_or_fill(Operator):
	bl_idname = "mesh.ke_bridge_or_fill"
	bl_label = "Bridge or Fill"
	bl_description = "Bridge, except when ONE continous border edge-loop is selected: Grid Fill. " \
					 "F2 mode with 1 EDGE or 1 VERT selected. " \
					 "FACE ADD with two edges (sharing a vert) or 3+ verts in vert mode."

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]

		obj = bpy.context.active_object
		mesh = obj.data
		obj.update_from_editmode()

		if sel_mode[0]:
			sel_verts = [v for v in mesh.vertices if v.select]
			if len(sel_verts) == 1:
				try: bpy.ops.mesh.f2('INVOKE_DEFAULT')
				except: bpy.ops.mesh.fill('INVOKE_DEFAULT')
			elif len(sel_verts) > 2:
				bpy.ops.mesh.edge_face_add()

		if sel_mode[1]:
			vert_pairs = []
			sel_edges = [e for e in mesh.edges if e.select]
			for e in sel_edges:
				vp = [v for v in e.vertices]
				vert_pairs.append(vp)

			if len(sel_edges) == 1:
				try: bpy.ops.mesh.f2('INVOKE_DEFAULT')
				except: bpy.ops.mesh.fill('INVOKE_DEFAULT')

			elif vert_pairs:
				if len(sel_edges) == 2:
					tri_check = len(list(set(vert_pairs[0] + vert_pairs[1])))
					if tri_check <4:
						bpy.ops.mesh.edge_face_add()

				check_loops = get_loops(vert_pairs, legacy=True)
				if len(check_loops) == 1 and check_loops[0][0] == check_loops[-1][-1]:
					try: bpy.ops.mesh.fill_grid('INVOKE_DEFAULT', True)
					except:
						try: bpy.ops.mesh.f2('INVOKE_DEFAULT')
						except: bpy.ops.mesh.fill('INVOKE_DEFAULT')
				else:
					try: bpy.ops.mesh.bridge_edge_loops('INVOKE_DEFAULT', True)
					except: pass

		return {'FINISHED'}


class MESH_OT_ke_maya_connect(Operator):
	bl_idname = "mesh.ke_maya_connect"
	bl_label = "Maya Connect"
	bl_description = "EDGE (or FACE) selection: Subdivide, VERTS: Connect Verts"
	bl_options = {'REGISTER', 'UNDO'}

	region = None
	rv3d = None
	screen_x = 0
	mtx = None
	mouse_pos = [0, 0]
	visited = []

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)


	def pick_closest_edge(self, edges):
		pick, prev = None, 9001
		for e in edges:
			emp = average_vector([self.mtx @ v.co for v in e.verts])
			p = location_3d_to_region_2d(self.region, self.rv3d, emp)
			dist = sqrt((self.mouse_pos[0] - p.x) ** 2 + (self.mouse_pos[1] - p.y) ** 2)
			if dist < prev:
				pick, prev = e, dist
		return pick

	def get_edge_rings(self, start_edge, sel):
		max_count = 1000
		ring_edges = []
		area_bools = []
		faces_visited = []

		for loop in start_edge.link_loops:
			abools = []
			start = loop
			edges = [loop.edge]

			i = 0
			while i < max_count:
				loop = loop.link_loop_radial_next.link_loop_next.link_loop_next

				if len(loop.face.edges) != 4:
					# self.nq_report += 1
					break

				if loop.face in sel:
					abools.append(True)
					faces_visited.extend([loop.face])
				else:
					abools.append(False)

				edges.append(loop.edge)

				if loop == start or loop.edge.is_boundary:
					break
				i += 1

			ring_edges.append(edges)
			area_bools.append(abools)

		nr = len(ring_edges)

		if nr == 2:
			# crappy workaround - better solution tbd
			if len(ring_edges[0]) == 1 and ring_edges[0][0] == start_edge:
				ring_edges = [ring_edges[1]]
				nr = 1
			elif len(ring_edges[1]) == 1 and ring_edges[1][0] == start_edge:
				ring_edges = [ring_edges[0]]
				nr = 1

		ring = []

		if nr == 1:
			# 1-directional (Border edge starts)
			ring = [start_edge]
			if len(area_bools[0]) == 0:
				ab = area_bools[1]
			else:
				ab = area_bools[0]

			for b, e in zip(ab, ring_edges[0][1:]):
				if b: ring.append(e)

		elif nr == 2:
			# Splicing bi-directional loops
			ring = [start_edge]
			for b, e in zip(area_bools[0], ring_edges[0][1:]):
				if b and e != start_edge: ring.append(e)

			rest = []
			for b, e in zip(area_bools[1], ring_edges[1][1:]):
				if b and e not in ring: rest.append(e)

			rest.reverse()
			ring = rest + ring

		return ring, list(set(faces_visited))


	def invoke(self, context, event):
		self.mouse_pos[0] = event.mouse_region_x
		self.mouse_pos[1] = event.mouse_region_y
		return self.execute(context)


	def execute(self, context):
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
		if sel_mode[0]:
			try:
				bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
			except:
				bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

		elif sel_mode[1]:
			# Sel check
			sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
			if not sel_obj:
				sel_obj = [context.object]

			tot = []
			report = []

			for obj in sel_obj:
				me = obj.data
				bm = bmesh.from_edit_mesh(me)
				bm.edges.ensure_lookup_table()

				sel = [e for e in bm.edges if e.select]
				if sel:
					tot.append(len(sel))
					for e in sel:
						e.select = False

					new_edges = bmesh.ops.subdivide_edges(bm, edges=sel, cuts=1, use_grid_fill=False)
					for e in new_edges['geom_inner']:
						e.select = True

					bmesh.update_edit_mesh(me)
				else:
					report.append(obj.name)

			if any(t == 1 for t in tot):
				# print("Single Edge selected - Switching to Vert Mode")
				bpy.ops.mesh.select_mode(type='VERT')
				sel_mode = (True, False, False)

			if report:
				r = ", ".join(report)
				self.report({"INFO"}, 'No edges selected on "%s"' % r)

		elif sel_mode[2]:

			for area in bpy.context.screen.areas:
				if area.type == 'VIEW_3D':
					self.region = area.regions[-1]
					self.rv3d = area.spaces.active.region_3d

			self.screen_x = int(self.region.width * .5)

			sel_obj = context.selected_objects[:]
			if not sel_obj:
				self.report({"INFO"}, "No objects selected!")
				return {'CANCELLED'}

			for obj in sel_obj:

				self.mtx = obj.matrix_world.copy()
				me = obj.data
				bm = bmesh.from_edit_mesh(me)
				bm.edges.ensure_lookup_table()

				sel_poly = [p for p in bm.faces if p.select]
				sel_verts = [v.index for v in bm.verts if v.select]

				if len(sel_poly) == 1:
					start_edge = self.pick_closest_edge(sel_poly[0].edges)
					ring, null = self.get_edge_rings(start_edge, sel_poly)

					for e in bm.edges:
						e.select = False

					new_edges = bmesh.ops.subdivide_edges(bm, edges=ring, cuts=1, use_grid_fill=False)
					for e in new_edges['geom_inner']:
						e.select = True

				elif len(sel_poly) > 1:
					p_edges = []
					for p in sel_poly:
						p_edges.extend(p.edges)

					shared_edges = get_duplicates(p_edges)
					sed_bkp = shared_edges.copy()

					if not shared_edges:
						self.report({"INFO"}, "Invalid (Discontinuous?) selection")
						return {"CANCELLED"}

					rings = []
					ring, self.visited = self.get_edge_rings(shared_edges[0], sel_poly)
					rings.append(ring)

					if (len(ring) - 2) != len(shared_edges):

						sel1 = [v.index for v in bm.verts if v.select]

						sanity = 9001
						shared_edges = [e for e in shared_edges if e not in ring]

						while shared_edges or sanity > 0:
							if shared_edges:
								ring, fvis = self.get_edge_rings(shared_edges[0], sel_poly)
								self.visited.extend(fvis)
								rings.append(ring)
								shared_edges = [e for e in shared_edges if e not in ring]
							else:
								break
							sanity -= 1

						# improvised solution here...as we go ;D
						occurances = [[x, self.visited.count(x)] for x in set(self.visited)]
						corners = []
						cedges = []
						for item in occurances:
							if item[1] > 1:
								corners.append(item[0])
								cedges.extend(item[0].edges)

						new_rings = []

						for r in rings:
							discard = []
							for e in r:
								if e not in sed_bkp and e in cedges:
									discard.append(e)

							c = [e for e in r if e not in discard]
							new_rings.append(c)

						rings = new_rings

						for e in bm.edges:
							e.select_set(False)

						for r in rings:
							for e in r:
								e.select_set(True)

						# I should find a cleaner bmesh solution for cornering, but meh...
						bpy.ops.mesh.subdivide('INVOKE_DEFAULT')

						bm.verts.ensure_lookup_table()
						sel2 = [v for v in bm.verts if v.select]

						bpy.ops.mesh.select_all(action="DESELECT")

						for v in sel2:
							if v.index not in sel1:
								v.select_set(True)

						bpy.ops.mesh.select_mode(type='VERT')

					else:
						# Sinple one-ring direction cut
						if rings:

							for e in bm.edges:
								e.select = False

							for ring in rings:
								new_edges = bmesh.ops.subdivide_edges(bm, edges=ring, cuts=1, use_grid_fill=False)
								for e in new_edges['geom_inner']:
									e.select = True

						bm.verts.ensure_lookup_table()

				else:
					self.report({"INFO"}, "Nothing selected?")
					return {"CANCELLED"}

				bmesh.update_edit_mesh(me)

		if not sel_mode[0]:
			bpy.ops.mesh.select_mode(type='EDGE')

		return {'FINISHED'}


class MESH_OT_ke_triple_connect_spin(Operator):
	bl_idname = "mesh.ke_triple_connect_spin"
	bl_label = "TripleConnectSpin"
	bl_description = "VERTS: Connect Verts, EDGE(s): Spin, FACE(s): Triangulate"
	bl_options = {'REGISTER', 'UNDO'}

	connect_mode: bpy.props.EnumProperty(
		items=[("PATH", "Vertex Path", "", 1),
			   ("PAIR", "Vertex Pair", "", 2)],
		name="Vertex Connect Mode",
		default="PATH")

	spin_mode: bpy.props.EnumProperty(
		items=[("CW", "Clockwise", "", 1),
			   ("CCW", "Counter Clockwise", "", 2)],
		name="Edge Spin Mode",
		default="CW")

	triple_mode: bpy.props.EnumProperty(
		items=[("BEAUTY", "Beauty Method", "", 1),
			   ("FIXED", "Fixed/Clip Method", "", 2)],
		name="Face Triangulation Mode",
		default="BEAUTY")

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		selection = False

		bpy.ops.object.mode_set(mode='OBJECT')
		for v in context.object.data.vertices:
			if v.select:
				selection = True
				break
		bpy.ops.object.mode_set(mode='EDIT')

		if selection:
				sel_mode = bpy.context.tool_settings.mesh_select_mode[:]

				if sel_mode[0]:
					if self.connect_mode == 'PATH':
						try:
							bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
						except:
							bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')
					elif self.connect_mode == 'PAIR':
						bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

				elif sel_mode[1]:
					if self.spin_mode == 'CW':
						bpy.ops.mesh.edge_rotate(use_ccw=False)
					elif self.spin_mode == 'CCW':
						bpy.ops.mesh.edge_rotate(use_ccw=True)

				elif sel_mode[2]:
					if self.triple_mode == 'BEAUTY':
						bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
					elif self.triple_mode == 'FIXED':
						bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED', ngon_method='CLIP')
		else:
			return {'CANCELLED'}

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
	MESH_OT_ke_contextslide,
)


def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()
