bl_info = {
	"name": "keContextOps",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 3, 7),
	"blender": (2, 80, 0),
}

import bpy
import bmesh
from math import copysign
from mathutils import Vector
from bpy.types import Operator
from .ke_utils import get_loops, mouse_raycast, get_selected

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
			bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='EDGES')
		elif sel_mode[2]:
			bpy.ops.mesh.inset('INVOKE_DEFAULT', use_outset=False, )

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
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
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
				# bpy.ops.mesh.dissolve_edges(use_verts=True)
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
		items=[("VERT", "Vertex Edit Mode", "", "VERT", 1),
			   ("EDGE", "Edge Edit Mode", "", "EDGE", 2),
			   ("FACE", "Face Edit Mode", "", "FACE", 3),
			   ("OBJECT", "Object Mode", "", "OBJECT", 4)],
		name="Edit Mode",
		default="FACE")

	mouse_pos = Vector((0, 0))

	def invoke(self, context, event):
		self.mouse_pos[0] = event.mouse_region_x
		self.mouse_pos[1] = event.mouse_region_y
		return self.execute(context)

	def execute(self, context):
		em = self.edit_mode
		mode = bpy.context.mode

		obj = get_selected(context)

		hit_obj = False
		mouse_over = bpy.context.scene.kekit.selmode_mouse

		if mouse_over:
			if context.object.type == 'MESH':
				bpy.ops.object.mode_set(mode="OBJECT")
			hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

			if hit_obj:
				layer_objects = context.view_layer.objects[:]

				for o in context.selected_objects:
					o.select_set(False)

				for o in layer_objects:
					if o.name == hit_obj.name:
						o.select_set(True)
						context.view_layer.objects.active = o
						break

				if em != "OBJECT":
					bpy.ops.object.mode_set(mode="EDIT")
					bpy.ops.mesh.select_mode(type=em)

			elif not hit_obj and obj:
				if em != "OBJECT":
					bpy.ops.object.mode_set(mode="EDIT")
					bpy.ops.mesh.select_mode(type=em)

		elif obj:
			if em != "OBJECT":
				if mode == 'OBJECT':
					bpy.ops.object.mode_set(mode="EDIT")
					bpy.ops.mesh.select_mode(type=em)
				else:
					bpy.ops.mesh.select_mode(type=em)
			else:
				if mode != 'OBJECT':
					bpy.ops.object.mode_set(mode="OBJECT")
				else:
					bpy.ops.object.mode_set(mode="EDIT")

		return {'FINISHED'}


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

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode)

	def execute(self, context):
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
		if sel_mode[0]:
			try:
				bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
			except:
				bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

		elif sel_mode[1] or sel_mode[2]:
			bpy.ops.mesh.subdivide('INVOKE_DEFAULT')
		return {'FINISHED'}


class MESH_OT_ke_triple_connect_spin(Operator):
	bl_idname = "mesh.ke_triple_connect_spin"
	bl_label = "TripleConnectSpin"
	bl_description = "VERTS: Connect Verts, EDGE(s): Spin, FACE(s): Triangulate"
	bl_options = {'REGISTER', 'UNDO'}

	connect_mode: bpy.props.EnumProperty(
		items=[("PATH", "Vertex Path", "", "PATH", 1),
			   ("PAIR", "Vertex Pair", "", "PAIR", 2)],
		name="Vertex Connect Mode",
		default="PATH")

	spin_mode: bpy.props.EnumProperty(
		items=[("CW", "Clockwise", "", "CW", 1),
			   ("CCW", "Counter Clockwise", "", "CCW", 2)],
		name="Edge Spin Mode",
		default="CW")

	triple_mode: bpy.props.EnumProperty(
		items=[("BEAUTY", "Beauty Method", "", "BEAUTY", 1),
			   ("FIXED", "Fixed/Clip Method", "", "FIXED", 2)],
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


class VIEW3D_OT_ke_vptransform(Operator):
	bl_idname = "view3d.ke_vptransform"
	bl_label = "VP-Transform"
	bl_description = "Runs Grab,Rotate or Scale with View Planes auto-locked based on your viewport rotation."
	bl_options = {'REGISTER'}

	transform: bpy.props.EnumProperty(
		items=[("TRANSLATE", "Translate", "", "TRANSLATE", 1),
			   ("ROTATE", "Rotate", "", "ROTATE", 2),
			   ("RESIZE", "Resize", "", "RESIZE", 3),
			   ("COPYGRAB", "Duplcate & Move", "", "COPYGRAB", 4),
			   ],
		name="Transform",
		default="TRANSLATE")

	world_only: bpy.props.BoolProperty(default=True)

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		self.world_only = bpy.context.scene.kekit.vptransform
		if self.world_only:
			bpy.ops.transform.select_orientation(orientation='GLOBAL')
		rm = context.space_data.region_3d.view_matrix
		v = Vector(rm[2])

		xz,xy,yz = Vector((0,1,0)), Vector((0,0,1)), Vector((1,0,0))

		dic = {(True,False,True): abs(xz.dot(v)), (True,True,False): abs(xy.dot(v)), (False,True,True): abs(yz.dot(v))}
		vplane = sorted(dic, key=dic.get)[-1]

		if self.transform == 'TRANSLATE':
			bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane)
		elif self.transform == 'ROTATE':
			bpy.ops.transform.rotate('INVOKE_DEFAULT', constraint_axis=vplane)
		elif self.transform == 'RESIZE':
			bpy.ops.transform.resize('INVOKE_DEFAULT', constraint_axis=vplane)
		elif self.transform == 'COPYGRAB':
			if context.mode == 'EDIT_MESH' and context.object.type == 'MESH':
				bpy.ops.mesh.duplicate('INVOKE_DEFAULT')
			elif context.mode == 'OBJECT':
				bpy.ops.object.duplicate('INVOKE_DEFAULT')
			else:
				return {'CANCELLED'}
			bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=vplane)

		return {'FINISHED'}


class VIEW3D_OT_ke_view_align_snap(Operator):
	bl_idname = "view3d.ke_view_align_snap"
	bl_label = "View Align Snap"
	bl_description = "Snap view to nearest Ortho. Contextual variant: To selected (toggle) if anything is selected."
	bl_options = {'REGISTER'}

	contextual: bpy.props.BoolProperty(default=False)

	def execute(self, context):
		sel = []
		slot = []
		if self.contextual:
			slot = bpy.context.scene.ke_vtoggle
			obj = get_selected(context)
			if obj:
				obj.update_from_editmode()
				sel = [v for v in obj.data.vertices if v.select]

		# ALIGN TO SELECTED (TOGGLE)
		if sel or sum(slot) != 0:
			bpy.ops.view3d.ke_view_align_toggle()
		# OR SNAP TO NEAREST ORTHO
		else:
			rm = context.space_data.region_3d.view_matrix
			v = Vector(rm[2])
			x, y, z = abs(v.x), abs(v.y), abs(v.z)

			if x > y and x > z:
				axis = copysign(1, v.x), 0, 0
			elif y > x and y > z:
				axis = 0, copysign(1, v.y), 0
			else:
				axis = 0, 0, copysign(1, v.z)

			# Negative: FRONT (-Y), LEFT(-X), BOTTOM (-Z)
			if sum(axis) < 0:
				if bool(axis[2]):
					bpy.ops.view3d.view_axis(type='BOTTOM')
				elif bool(axis[1]):
					bpy.ops.view3d.view_axis(type='FRONT')
				else:
					bpy.ops.view3d.view_axis(type='LEFT')
			else:
				if bool(axis[2]):
					bpy.ops.view3d.view_axis(type='TOP')
				elif bool(axis[1]):
					bpy.ops.view3d.view_axis(type='BACK')
				else:
					bpy.ops.view3d.view_axis(type='RIGHT')

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
	VIEW3D_OT_ke_vptransform,
	MESH_OT_ke_contextslide,
	VIEW3D_OT_ke_view_align_snap
)


def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()
