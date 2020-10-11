bl_info = {
	"name": "keDirectLoopCut",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 3, 5),
	"blender": (2, 80, 0),
}
import bpy
import bmesh
from .ke_utils import get_distance, mouse_raycast, flatten
from mathutils.geometry import intersect_point_line


def get_edge_ring_loops(loop, max_count=1000):
	rings = [loop]
	i = 0
	while i < max_count:
		loop = loop.link_loop_radial_next.link_loop_next.link_loop_next
		if loop == rings[0]:
			break
		elif len(loop.face.edges) != 4:
			break
		else:
			rings.append(loop)
			if loop.edge.is_boundary:
				break
			i += 1
	return rings


def get_vert_link(er, targetvert):
	prev = targetvert
	loop_verts = []
	for r in er:
		for v in r.verts[:]:
			for e in v.link_edges:
				if e.other_vert(v) == prev and e != r:
					prev = v
					loop_verts.append(e.verts[:])
					break
	return [i for i in flatten(loop_verts)]


def sort_ring(edge, targetvert, center=False):
	tvs = []
	loops = edge.link_loops
	if len(loops) == 2:
		loop1, loop2 = edge.link_loops[0], edge.link_loops[1]
		l1 = [loop.edge for loop in get_edge_ring_loops(loop1)]
		l2 = [loop.edge for loop in get_edge_ring_loops(loop2)]
		if len(l1) > len(l2):
			l2 = [i for i in l2 if i not in l1]
			sr = l2 + l1
			if not center:
				vl1 = get_vert_link(l1, targetvert)
				vl2 = get_vert_link(l2, targetvert)
				tvs = list(set(vl1 + vl2))

		elif len(l2) > len(l1):
			l2 = [i for i in l2 if i not in l1]
			sr = l1 + l2
			if not center:
				vl1 = get_vert_link(l1, targetvert)
				vl2 = get_vert_link(l2, targetvert)
				tvs = list(set(vl1 + vl2))
		else:
			sr = l1
			if not center:
				tvs = get_vert_link(l1, targetvert)
	else:
		sr = [loop.edge for loop in get_edge_ring_loops(loops[0])]
		if not center:
			tvs = get_vert_link(sr, targetvert)

	return sr, tvs


class MESH_OT_ke_direct_loop_cut(bpy.types.Operator):
	bl_idname = "mesh.ke_direct_loop_cut"
	bl_label = "Direct Loop Cut"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_description = "Adds edge loop under mouse pointer -or- edge-center (on selected) if over nothing." \
					 "Select one edge to add loop to ring, or select manual ring to limit cut. Also: Multi-ring slice."
	bl_options = {'REGISTER'}

	mode : bpy.props.EnumProperty(items=[("DEFAULT", "Default", ""),("SLIDE", "Slide", "")],
								  name="Mode", default="DEFAULT")
	mouse_pos = [0, 0]

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)


	def invoke(self, context, event):
		self.mouse_pos[0] = event.mouse_region_x
		self.mouse_pos[1] = event.mouse_region_y
		return self.execute(context)


	def execute(self, context):
		bpy.ops.mesh.select_mode(type='EDGE')
		me = context.object.data
		obj_mtx = context.object.matrix_world

		bpy.ops.object.mode_set(mode="OBJECT")
		sel_edge = [e for e in me.edges if e.select]
		hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)
		bpy.ops.object.mode_set(mode="EDIT")

		if self.mode == "DEFAULT":
			if context.object == hit_obj or hit_wloc:
				bpy.ops.mesh.select_all(action='DESELECT')
				sel_edge = []

		bm = bmesh.from_edit_mesh(me)
		bm.edges.ensure_lookup_table()

		# SELECTIONS ---------------------------------------------------------------------------------
		multi_sel, multi_split, rings = False, False, []
		c = len(sel_edge)

		if sel_edge and c == 1:
			sel_edge = bm.edges[sel_edge[0].index]

		elif sel_edge and c > 1:
			if hit_wloc:
				sel_edges = [e for e in bm.edges if e.select]
				bm.select_flush(False)
				sel_edge = False
				if len(sel_edges) >= 2:
					multi_sel = True
			else:
				sel_edges = [e for e in bm.edges if e.select]
				sel_edge = sel_edges[-1]
				multi_sel = True

		if not sel_edge:
			bpy.ops.view3d.select(extend=True, location=self.mouse_pos)
			bm.edges.ensure_lookup_table()
			sel_edge = [e for e in bm.edges if e.select]
			if not sel_edge:
				self.report(type={"INFO"}, message="No edge selection found!")
				return {'CANCELLED'}
			else:
				sel_edge = sel_edge[0]

		# CUT DIRECTION	 -----------------------------------------------------------------------------
		# Set direction-vert nearest mouse to [0] and get fac 0-1 value, unless raycast fail -> 0.5
		edge_verts = sel_edge.verts[:]

		if hit_wloc:
			edge_points = [obj_mtx @ v.co for v in edge_verts]

			d1, d2 = get_distance(hit_wloc, edge_points[0]), get_distance(hit_wloc, edge_points[1])
			if d1 > d2:
				edge_points.reverse()
				edge_verts.reverse()

			mouse_point, fac = intersect_point_line(hit_wloc, edge_points[0], edge_points[1])
		else:
			fac = 0.5

		ring, target_verts = sort_ring(sel_edge, edge_verts[0])
		# print ("SORTRING:", [e.index for e in ring], "TARGETVERTS:", [v.index for v in target_verts] )
		rings = [ring]

		# Check if user selection is on the ring -or- multi edge slice
		if multi_sel:
			ring_check = [e for e in sel_edges if e in ring and e != sel_edge]
			comp_ring = [sel_edge] + ring_check

			if len(ring_check) >= 1 and set(comp_ring) == set(sel_edges):
				# print("Ring matches selected - Capping ring to selection")
				rings[0] = comp_ring
			elif len(ring_check) >= 1:
				# Probably not sequential ring selection...skip for now
				self.report(type={"INFO"}, message="Invalid edge selection?")
				return {'CANCELLED'}
			else:
				# print("Multi Edge Split mode")
				multi_split = True
				more_rings = [e for e in sel_edges if e != sel_edge]
				for r in more_rings:
					r, tvs = sort_ring(r, edge_verts[0], center=True)
					rings.append(r)

		# Cut Rings ------------------------------------------------------------------------------------------
		new_edges = []
		for edge_ring in rings:
			new_verts = []
			for edge in edge_ring:

				if not multi_split:
					ep = edge.verts[:]
					if ep[0] not in target_verts:
						ep.reverse()
					nedge, nvert = bmesh.utils.edge_split(edge, ep[0], fac)
					bmesh.update_edit_mesh(me)
					new_verts.append(nvert)

				elif multi_split:
					nedge, nvert = bmesh.utils.edge_split(edge, edge.verts[0], 0.5)
					bmesh.update_edit_mesh(me)
					new_verts.append(nvert)

				bm.verts.index_update()

			# make new edge loop
			nedges = bmesh.ops.connect_verts(bm, verts=new_verts)
			bmesh.update_edit_mesh(me)
			nedges = [e for e in nedges.values()][0]
			new_edges.append(nedges)

		new_edges = [e for e in flatten(new_edges)]

		# clear selections
		bpy.ops.mesh.select_all(action="DESELECT")
		bm.edges.ensure_lookup_table()

		# select and/or slide ?
		for e in new_edges:
			e.select = True

		# bmesh.update_edit_mesh(me)
		me.update()
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode="EDIT")
		# Todo: ok something is a bit fishy with this BM...seems to work when toggling for now...

		if self.mode == "SLIDE":
			bpy.ops.transform.edge_slide("INVOKE_DEFAULT")

		return {"FINISHED"}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (MESH_OT_ke_direct_loop_cut,
		   )

def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()
