bl_info = {
	"name": "kekit_view_tools",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 0, 2),
	"blender": (2, 80, 0),
}
import bpy
import bmesh
from math import copysign, radians
from mathutils import Vector, Quaternion, Matrix
from .ke_utils import average_vector, correct_normal, get_distance, get_selected, getset_transform, restore_transform
from bpy.types import Operator


def sort_vert_order(vcoords):
	sq = False
	vp = vcoords[0], vcoords[1], vcoords[2]
	vp1 = get_distance(vp[0], vp[1])
	vp2 = get_distance(vp[0], vp[2])
	vp3 = get_distance(vp[1], vp[2])
	if round(vp1, 4) == round(vp2, 4):
		sq = True
	vpsort = {"2": vp1, "1": vp2, "0": vp3}
	s = [int(i) for i in sorted(vpsort, key=vpsort.__getitem__)]
	s.reverse()
	return [vcoords[s[0]], vcoords[s[1]], vcoords[s[2]]], sq


class VIEW3D_OT_ke_view_align(Operator):
	bl_idname = "view3d.ke_view_align"
	bl_label = "View Align Selected"
	bl_description = "Align View to Active Face or 3 vertices."
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH' and
				context.object.data.is_editmode and
				context.space_data.type == "VIEW_3D")

	def execute(self, context):
		# SETUP & SELECTIONS
		w = Vector((0, 0, 1))
		sel_verts = []
		rv3d = context.space_data.region_3d
		sel_mode = bpy.context.tool_settings.mesh_select_mode[:]

		o = context.object
		obj_mtx = o.matrix_world

		bm = bmesh.from_edit_mesh(o.data)
		active = bm.faces.active
		face_mode = False
		if active and sel_mode[2]:
			if len(active.verts) == 3:
				sel_verts = active.verts[:]
			else:
				sel_verts = active.verts[:]
				face_mode = True
		else:
			sel_poly = [p for p in bm.faces if p.select]
			if sel_poly:
				sel_verts = [v for v in sel_poly[0].verts]
			else:
				sel_verts = [v for v in bm.verts if v.select]

		if not sel_verts or len(sel_verts) < 3:
			self.report(type={'INFO'}, message="Nothing selected?")
			return {'CANCELLED'}

		if face_mode:
			n = correct_normal(obj_mtx, active.normal)
			t = correct_normal(obj_mtx, active.calc_tangent_edge())

			c = t.cross(w)
			if c.dot(n) < 0:
				t.negate()
			b = n.cross(t).normalized()

			unrotated = Matrix((t, b, n)).to_4x4().inverted().to_quaternion()
			avg_pos = obj_mtx @ active.calc_center_median()

		else:
			# SORT 3 VERTICES ORDER FOR BEST ANGLES FOR TANGENT & BINORMAL (Disregard hypothenuse)
			vec_poslist_sort = sort_vert_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
			vec_poslist = vec_poslist_sort[0]
			p1, p2, p3 = obj_mtx @ vec_poslist[0], obj_mtx @ vec_poslist[1], obj_mtx @ vec_poslist[2]
			v_1 = p2 - p1
			v_2 = p3 - p1

			# If square, switch t & b
			if vec_poslist_sort[1]:
				t1 = v_1.dot(w)
				t2 = v_2.dot(w)
				if t2 > t1:
					v_1, v_2 = v_2, v_1
			else:
				v_1.negate()

			n = v_1.cross(v_2).normalized()

			# n direction flip check
			fn = average_vector([v.normal for v in sel_verts])
			fn = correct_normal(obj_mtx, fn)

			check = n.dot(fn.normalized())
			if check <= 0:
				n.negate()
				v_1.negate()
				v_2.negate()

			# additional direction check to avoid some rotation issues
			if v_1.dot(w) < 0:
				v_1.negate()

			# CREATE VIEW ROTATION & LOCATION & APPLY
			avg_pos = obj_mtx @ average_vector(vec_poslist)
			b = v_1.cross(n).normalized()
			unrotated = Matrix((b, v_1, n)).to_4x4().inverted().to_quaternion()

		rv3d.view_rotation = unrotated
		rv3d.view_location = avg_pos

		bmesh.update_edit_mesh(o.data, True)

		return {'FINISHED'}


class VIEW3D_OT_ke_view_align_toggle(Operator):
	bl_idname = "view3d.ke_view_align_toggle"
	bl_label = "View Align Selected Toggle"
	bl_description = "Selected: Active Face OR 3 Vertices OR 2 Edges (or in Object-mode: Obj's Z axis)" \
					 "\nCursor: Use after Cursor Fit&Align.\nToggle (run again) to restore view from before alignment."
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.EnumProperty(
		items=[("SELECTION", "", "", 1),
			   ("CURSOR", "", "", 2),
			   ],
		name="View Align Mode", options={'HIDDEN'},
		default="SELECTION")

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	def execute(self, context):
		rv3d = context.space_data.region_3d
		v = [0,0,0,0,0,0,0,0,0]
		slot = bpy.context.scene.ke_vtoggle
		# SET
		if sum(slot) == 0:
			p = [int(rv3d.is_perspective)]
			d = [rv3d.view_distance]
			loc = [i for i in rv3d.view_location]
			rot = [i for i in rv3d.view_rotation]
			v = p + d + loc + rot
			slot[0] = v[0]
			slot[1] = v[1]
			slot[2] = v[2]
			slot[3] = v[3]
			slot[4] = v[4]
			slot[5] = v[5]
			slot[6] = v[6]
			slot[7] = v[7]
			slot[8] = v[8]

			if self.mode == "SELECTION":
				if context.object.mode == "EDIT":
					bpy.ops.view3d.ke_view_align()
				else:
					bpy.ops.view3d.view_axis(type='TOP', align_active=True)

			elif self.mode == "CURSOR":
				c = context.scene.cursor
				rv3d.view_rotation = c.rotation_quaternion

			bpy.ops.view3d.view_selected(use_all_regions=False)
			if rv3d.is_perspective:
				bpy.ops.view3d.view_persportho()
		else:
			v[0] = slot[0]
			v[1] = slot[1]
			v[2] = slot[2]
			v[3] = slot[3]
			v[4] = slot[4]
			v[5] = slot[5]
			v[6] = slot[6]
			v[7] = slot[7]
			v[8] = slot[8]

			if not rv3d.is_perspective and bool(v[0]):
				bpy.ops.view3d.view_persportho()
			rv3d.view_distance = v[1]
			rv3d.view_location = Vector(v[2:5])
			rv3d.view_rotation = Quaternion(v[5:9])

			slot[0] = 0
			slot[1] = 0
			slot[2] = 0
			slot[3] = 0
			slot[4] = 0
			slot[5] = 0
			slot[6] = 0
			slot[7] = 0
			slot[8] = 0

		return {"FINISHED"}


class VIEW3D_OT_ke_viewpos(Operator):
	bl_idname = "view3d.ke_viewpos"
	bl_label = "Get & Set Viewpos"
	bl_description = "Get & Set Viewpos"
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.EnumProperty(
		items=[("GET", "Get Viewpos", "", "GET", 1),
			   ("SET", "Set Viewpos", "", "SET", 2),
			   ],
		name="Viewpos", options={"HIDDEN"},
		default="SET")

	@classmethod
	def description(cls, context, properties):
		if properties.mode == "GET":
			return "Get Viewport placement values"
		else:
			return "Set Viewport placement values"

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	def execute(self, context):
		rv3d = context.space_data.region_3d

		if self.mode == "GET":
			p = [int(rv3d.is_perspective)]
			d = [rv3d.view_distance]
			loc = [i for i in rv3d.view_location]
			rot = [i for i in rv3d.view_rotation]
			v = p + d + loc + rot
			v = str(v)
			bpy.context.scene.ke_query_props.view_query = v

		else:
			v = [0]
			try:
				q = str(bpy.context.scene.ke_query_props.view_query)[1:-1]
				qs = q.split(",")
				v = [float(i) for i in qs]
			except:
				print("Incorrect values. Aborting.")
				return {'CANCELLED'}

			if len(v) == 9:
				if not rv3d.is_perspective and bool(v[0]):
					bpy.ops.view3d.view_persportho()
				rv3d.view_distance = v[1]
				rv3d.view_location = Vector(v[2:5])
				rv3d.view_rotation = Quaternion(v[5:9])

		return {'FINISHED'}


class VIEW3D_OT_ke_view_bookmark(Operator):
	bl_idname = "view3d.ke_view_bookmark"
	bl_label = "View Bookmarks"
	bl_description = "Store & Use Viewport Placement (persp/ortho, loc, rot)"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.EnumProperty(
		items=[("SET1", "Set Cursor Slot 1", "", "SET1", 1),
			   ("SET2", "Set Cursor Slot 2", "", "SET2", 2),
			   ("SET3", "Set Cursor Slot 3", "", "SET3", 3),
			   ("SET4", "Set Cursor Slot 4", "", "SET4", 4),
			   ("SET5", "Set Cursor Slot 5", "", "SET5", 5),
			   ("SET6", "Set Cursor Slot 6", "", "SET6", 6),
			   ("USE1", "Use Cursor Slot 1", "", "USE1", 7),
			   ("USE2", "Use Cursor Slot 2", "", "USE2", 8),
			   ("USE3", "Use Cursor Slot 3", "", "USE3", 9),
			   ("USE4", "Use Cursor Slot 4", "", "USE4", 10),
			   ("USE5", "Use Cursor Slot 5", "", "USE5", 11),
			   ("USE6", "Use Cursor Slot 6", "", "USE6", 12)
			   ],
		name="View Bookmarks", options={"HIDDEN"},
		default="SET1")

	@classmethod
	def description(cls, context, properties):
		if properties.mode in {"SET1", "SET2","SET3", "SET4", "SET5", "SET6"}:
			return "Store Viewport placement in slot " + properties.mode[-1]
		else:
			return "Recall Viewport placement from slot " + properties.mode[-1]

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	def execute(self, context):
		rv3d = context.space_data.region_3d
		v = [0,0,0,0,0,0,0,0,0]

		nr = int(self.mode[-1])
		if nr == 2:
			slot = bpy.context.scene.ke_vslot2
		elif nr == 3:
			slot = bpy.context.scene.ke_vslot3
		elif nr == 4:
			slot = bpy.context.scene.ke_vslot4
		elif nr == 5:
			slot = bpy.context.scene.ke_vslot5
		elif nr == 6:
			slot = bpy.context.scene.ke_vslot6
		else:
			slot = bpy.context.scene.ke_vslot1

		if "SET" in self.mode:
			p = [int(rv3d.is_perspective)]
			d = [rv3d.view_distance]
			loc = [i for i in rv3d.view_location]
			rot = [i for i in rv3d.view_rotation]
			v = p + d + loc + rot
			if v == list(slot):
				# "Clearing" slot if assigning the same view as stored
				v = [0,0,0,0,0,0,0,0,0]
			# todo: assigning a list of floats to floatvec-prop in one line?
			slot[0] = v[0]
			slot[1] = v[1]
			slot[2] = v[2]
			slot[3] = v[3]
			slot[4] = v[4]
			slot[5] = v[5]
			slot[6] = v[6]
			slot[7] = v[7]
			slot[8] = v[8]
			bpy.context.scene.ke_vbcycle = nr - 1
		else:
			# USE
			v[0] = slot[0]
			v[1] = slot[1]
			v[2] = slot[2]
			v[3] = slot[3]
			v[4] = slot[4]
			v[5] = slot[5]
			v[6] = slot[6]
			v[7] = slot[7]
			v[8] = slot[8]

			if sum(v) != 0:
				bpy.context.scene.ke_vbcycle = nr - 1
				if not rv3d.is_perspective and bool(v[0]):
					bpy.ops.view3d.view_persportho()
				rv3d.view_distance = v[1]
				rv3d.view_location = Vector(v[2:5])
				rv3d.view_rotation = Quaternion(v[5:9])
			else:
				print("View Bookmark: Empty slot - cancelled")

		return {"FINISHED"}


class VIEW3D_OT_ke_view_bookmark_cycle(Operator):
	bl_idname = "view3d.ke_view_bookmark_cycle"
	bl_label = "Cycle View Bookmarks"
	bl_description = "Cycle stored Viewport Bookmarks"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

	def execute(self, context):
		slots = [bool(sum(bpy.context.scene.ke_vslot1)), bool(sum(bpy.context.scene.ke_vslot2)),
				 bool(sum(bpy.context.scene.ke_vslot3)), bool(sum(bpy.context.scene.ke_vslot4)),
				 bool(sum(bpy.context.scene.ke_vslot5)), bool(sum(bpy.context.scene.ke_vslot6))]

		current = int(bpy.context.scene.ke_vbcycle)

		if any(slots):

			available = []
			next_slot = None

			for i, slot in enumerate(slots):
				if slot:
					available.append(i)
					if i > current:
						next_slot = i
						break

			if next_slot is None and available:
				next_slot = available[0]

			if next_slot is not None:
				bpy.context.scene.ke_vbcycle = next_slot
				bpy.ops.view3d.ke_view_bookmark(mode = "USE" + str(next_slot + 1))

		return {"FINISHED"}


class VIEW3D_OT_ke_view_align_snap(Operator):
	bl_idname = "view3d.ke_view_align_snap"
	bl_label = "View Align Snap"
	bl_description = "Snap view to nearest Orthographic. Note: No toggle - just rotate view to perspective"
	bl_options = {'REGISTER'}

	contextual: bpy.props.BoolProperty(default=False)

	@classmethod
	def poll(cls, context):
		return context.space_data.type == "VIEW_3D"

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


class VIEW3D_OT_ke_vp_step_rotate(Operator):
	bl_idname = "view3d.ke_vp_step_rotate"
	bl_label = "VP Step Rotate"
	bl_description = "Rotate object or selected elements given angle, based on viewport viewplane (Global Only)"
	bl_space_type = 'VIEW_3D'
	bl_options = {'REGISTER', 'UNDO'}

	mode: bpy.props.EnumProperty(
		items=[("ROT090", "Rotate 90", "", "ROT90", 1),
			   ("NROT090", "Rotate -90", "", "NROT90", 2),
			   ("ROT045", "Rotate 45", "", "ROT45", 3),
			   ("NROT045", "Rotate -45", "", "NROT45", 4),
			   ("ROT180", "Rotate 180", "", "ROT180", 5),
			   ("NROT180", "Rotate -180", "", "NROT180", 6),
			   ],
		name="Mode",
		default="ROT090")

	@classmethod
	def poll(cls, context):
		return context.object is not None and context.space_data.type == "VIEW_3D"

	def execute(self, context):
		# extract user direction
		val = int(self.mode[-3:])
		if self.mode[0] == "N":
			val *= -1

		# get viewport rel to world axis and rotate
		rm = context.space_data.region_3d.view_matrix
		v = Vector(rm[2]).to_3d()

		x = v.dot(Vector((1, 0, 0)))
		y = v.dot(Vector((0, 1, 0)))
		z = v.dot(Vector((0, 0, 1)))

		xa, ya, za = abs(x), abs(y), abs(z)

		if xa > ya and xa > za:
			if val < 0 and x < 0 or val > 0 > x:
				val *= -1
			axis = True, False, False
			oa = "X"
		elif ya > xa and ya > za:
			if val < 0 and y < 0 or val > 0 > y:
				val *= -1
			axis = False, True, False
			oa = "Y"
		else:
			if val < 0 and z < 0 or val > 0 > z:
				val *= -1
			axis = False, False, True
			oa = "Z"

		bpy.ops.transform.rotate(value=radians(val), orient_axis=oa, orient_type='GLOBAL', orient_matrix_type='GLOBAL',
								 constraint_axis=axis, mirror=True, use_proportional_edit=False,
								 proportional_edit_falloff='SMOOTH', proportional_size=1,
								 use_proportional_connected=False, use_proportional_projected=False)
		return {"FINISHED"}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	VIEW3D_OT_ke_view_bookmark,
	VIEW3D_OT_ke_view_align,
	VIEW3D_OT_ke_view_align_toggle,
	VIEW3D_OT_ke_viewpos,
	VIEW3D_OT_ke_view_align_snap,
	VIEW3D_OT_ke_vp_step_rotate,
	VIEW3D_OT_ke_view_bookmark_cycle
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

	bpy.types.Scene.ke_vslot1 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vslot2 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vslot3 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vslot4 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vslot5 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vslot6 = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vtoggle = bpy.props.FloatVectorProperty(size=9)
	bpy.types.Scene.ke_vbcycle = bpy.props.IntProperty(default=0, min=0, max=5)


def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

	try:
		del bpy.types.Scene.ke_vslot1
		del bpy.types.Scene.ke_vslot2
		del bpy.types.Scene.ke_vslot3
		del bpy.types.Scene.ke_vslot4
		del bpy.types.Scene.ke_vslot5
		del bpy.types.Scene.ke_vslot6
		del bpy.types.Scene.ke_vtoggle
		del bpy.types.Scene.ke_vbcycle

	except Exception as e:
		print('unregister fail:\n', e)
		pass


if __name__ == "__main__":
	register()
