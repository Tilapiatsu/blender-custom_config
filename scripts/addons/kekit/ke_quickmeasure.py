bl_info = {
	"name": "keQuickMeasure",
	"author": "Kjell Emanuelsson",
	"category": "Modeling",
	"version": (1, 3, 6),
	"blender": (2, 80, 0),
}
import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from math import ceil
from bpy_extras.view3d_utils import location_3d_to_region_2d
from .ke_utils import get_distance, get_midpoint


def bb(self, context):
	self.stat = []
	x, y, z = [], [], []
	for i in self.vpos:
		x.append(i[0])
		y.append(i[1])
		z.append(i[2])
	x, y, z = sorted(x), sorted(y), sorted(z)
	if len(x) > 1:
		self.area = str(round((x[-1] - x[0]) * (y[-1] - y[0]), 4)) + "\u00b2"
	self.lines = [
		((x[0], y[0], z[0]), (x[0], y[0], z[-1])),
		((x[0], y[0], z[0]), (x[-1], y[0], z[0])),
		((x[0], y[0], z[0]), (x[0], y[-1], z[0]))
	]
	self.bb_lines = [
		((x[-1], y[-1], z[-1]), (x[-1], y[-1], z[0])),
		((x[-1], y[-1], z[-1]), (x[0], y[-1], z[-1])),
		((x[-1], y[-1], z[-1]), (x[-1], y[0], z[-1])),
		((x[0], y[0], z[-1]), (x[0], y[-1], z[-1])),
		((x[0], y[-1], z[0]), (x[0], y[-1], z[-1])),
		((x[-1], y[0], z[0]), (x[-1], y[0], z[-1])),
		((x[0], y[0], z[-1]), (x[-1], y[0], z[-1])),
		((x[0], y[-1], z[0]), (x[-1], y[-1], z[0])),
		((x[-1], y[-1], z[0]), (x[-1], y[0], z[0])),
	]
	for i in self.lines:
		d = round(get_distance(i[0], i[1]), 4)
		self.stat.append(d)


def sel_check(self, context):
	self.edit_mode = bpy.context.tool_settings.mesh_select_mode[:]
	self.vpos = []
	self.lines = []
	self.stat = []
	self.bb_lines = []
	self.obj_mode = False

	if context.object.data.is_editmode:

		# Vert mode check
		if self.edit_mode[0]:
			for obj in context.selected_editable_objects:
				mat = obj.matrix_world
				mesh = obj.data
				obj.update_from_editmode()

				if self.vertmode == "Distance":
					sel_verts = [v for v in mesh.vertices if v.select]
					if sel_verts:
						vpos = [mat @ v.co for v in sel_verts]
						self.vpos.extend(vpos)
				else:  #bbox
					verts = [v for v in mesh.vertices if v.select]
					self.vpos.extend([mat @ v.co for v in verts])

			if self.vertmode == "Distance" and len(self.vpos) > 1:
				self.stat = [round(get_distance(self.vpos[0], self.vpos[1]), 4)]
				self.lines = [(self.vpos[0], self.vpos[1])]

			elif self.vertmode == "BBox" and len(self.vpos) > 1:
				bb(self, context)

			else:
				self.lines = None

		# Edge mode check
		elif self.edit_mode[1]:
			for obj in context.selected_editable_objects:
				mat = obj.matrix_world
				mesh = obj.data
				obj.update_from_editmode()

				edges = [e for e in mesh.edges if e.select]
				if edges:
					for e in edges:
						vps = []
						idx = [v for v in e.vertices]
						for i in idx:
							vps.append(mat @ mesh.vertices[i].co)
						self.lines.append(vps)
						self.stat.append(round(get_distance(vps[0], vps[1]), 4))

		# Poly mode check
		elif self.edit_mode[2]:
			for obj in context.selected_editable_objects:
				mat = obj.matrix_world
				mesh = obj.data
				obj.update_from_editmode()

				verts = [v for v in mesh.vertices if v.select]
				self.vpos.extend([mat @ v.co for v in verts])

			if len(self.vpos) < 3:
				self.lines = None
			else:
				bb(self,context)

	else:  # Object mode check
		vc = []
		for o in context.selected_objects :
			if o.type == "MESH":
				vc.extend([o.matrix_world @ v.co for v in o.data.vertices])
		self.vpos = vc
		if self.vpos:
			bb(self, context)


def txt_calc(self, context):
	upd = []
	for i in self.lines:
		line_mid = get_midpoint(i[0], i[1])
		tpos = location_3d_to_region_2d(context.region, context.space_data.region_3d, line_mid)
		upd.append(tpos)
	self.txt_pos = upd


def draw_callback_view(self, context):
	if self.lines:
		glines = []
		bblines = []

		if self.edit_mode[2] or self.obj_mode or self.vertmode == "BBox":
			for i in self.bb_lines:
				bblines.extend((i[0], i[1]))

		for i in self.lines:
			if bblines:
				glines.append((i[0], i[1]))
			else:
				glines.extend((i[0], i[1]))

		shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
		bgl.glEnable(bgl.GL_BLEND)
		bgl.glLineWidth(3)

		if bblines:
			z = batch_for_shader(shader, 'LINES', {"pos": glines[0]})
			shader.bind()
			shader.uniform_float("color", (0.12, 0.43, 0.76, 0.85))
			z.draw(shader)

			x = batch_for_shader(shader, 'LINES', {"pos": glines[1]})
			shader.bind()
			shader.uniform_float("color", (0.83, 0.05, 0.17, 0.85))
			x.draw(shader)

			y = batch_for_shader(shader, 'LINES', {"pos": glines[2]})
			shader.bind()
			shader.uniform_float("color", (0.45, 0.61, 0.27, 0.85))
			y.draw(shader)

			batch = batch_for_shader(shader, 'LINES', {"pos": bblines})
			shader.bind()
			shader.uniform_float("color", (0.65, 0.65, 0.65, 0.7))
			# shader.uniform_float("color", (0.86, 0.45, 0.06, 0.65))
			batch.draw(shader)

		else:
			batch = batch_for_shader(shader, 'LINES', {"pos": glines})
			shader.bind()
			shader.uniform_float("color", (0.3, 0.79, 0.74, 0.85))
			batch.draw(shader)

		bgl.glLineWidth(1)
		bgl.glDisable(bgl.GL_BLEND)


def draw_callback_px(self, context):
	font_id = 0

	if self.lines:
		# draw stats
		count = 0
		blf.enable(font_id, 4)
		blf.size(font_id, 14, 72)
		blf.shadow(font_id, 3, 0, 0, 0, 1)
		blf.shadow_offset(font_id, 1, -1)

		for t, s in zip(self.txt_pos, self.stat):
			blf.position(font_id, t[0], t[1], 0)
			if self.edit_mode[2] or self.obj_mode or self.vertmode == "BBox" and not self.edit_mode[1]:
				if   count == 0: axis = "z:"
				elif count == 1: axis = "x:"
				elif count == 2: axis = "y:"
				s = axis + str(s)
			blf.draw(font_id, str(s))
			count += 1

	# Selection Info
	hpos, vpos = self.screen_x - 100, 64
	blf.shadow(font_id, 5, 0, 0, 0, 1)
	blf.shadow_offset(font_id, 1, -1)

	if not self.lines:
		blf.color(font_id, 0.5, 0.5, 0.5, 1)
		blf.size(font_id, 15, 72)
		blf.position(font_id, hpos, vpos + 86, 0)
		blf.draw(font_id, "[ Invalid Selection ]")
	else:
		blf.color(font_id, 0.796, 0.7488, 0.6435, 1)
		blf.size(font_id, 20, 72)
		blf.position(font_id, hpos, vpos + 86, 0)

		if self.edit_mode[1] and not self.obj_mode:
			t = ceil(sum(self.stat * 10000)) / 10000
			blf.draw(font_id, "Quick Measure  [Edges Total: %s]" % str(t))
		elif self.edit_mode[0] and not self.obj_mode:
			if self.vertmode == "Distance":
				blf.draw(font_id, "Quick Measure [Vert Mode: %s]"  % self.vertmode)
			else:
				blf.draw(font_id, "Quick Measure [Vert Mode: %s] Area XY: %s"  % (self.vertmode, self.area) )
		else:
			blf.draw(font_id, "Quick Measure [Area XY: %s]" % self.area)

	# Instructions
	blf.color(font_id, 0.8, 0.8, 0.8, 1)
	blf.size(font_id, 15, 72)
	blf.position(font_id, hpos, vpos + 56, 0)
	blf.draw(font_id, "Change / Update Mode: 1-Verts, 2-Edges, 3-Faces, 4-Objects")
	blf.position(font_id, hpos, vpos + 16, 0)
	if self.edit_mode[0]:
		blf.draw(font_id, "Stop: Esc, Enter, Spacebar.      Toggle Vert Mode: V")
	else:
		blf.draw(font_id, "Stop: Esc, Enter, Spacebar")

	blf.position(font_id, hpos, vpos + 36, 0)
	blf.draw(font_id, "(G)rab, (R)otate, (S)cale. +XYZ +'>'")

	blf.color(font_id, 0.5, 0.5, 0.5, 1)
	blf.size(font_id, 12, 72)
	# blf.position(font_id, hpos, vpos + 15, 0)
	# if self.auto_update:
	# 	updmode = "Automatic Update"
	# else:
	# 	updmode = "Manual Update"
	# blf.draw(font_id, "Current Update Mode: %s   S: Toggle Auto/Manual" % updmode)
	blf.position(font_id, hpos, vpos - 3, 0)
	blf.draw(font_id, "Navigation: Blender(MMB) or Ind.Std(Alt-). 'TAB' toggles, '4' sets/updates Object.")


class VIEW3D_OT_ke_quickmeasure(bpy.types.Operator):
	bl_idname = "view3d.ke_quickmeasure"
	bl_label = "Quick Measure"
	bl_description = "Contextual measurement types by mesh selection (Obj & Edit modes)"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		return (context.object is not None and
				context.object.type == 'MESH')

	_handle = None
	_handle_px = None
	lines = None
	bb_lines = None
	txt_pos = []
	vpos = None
	vpairs = None
	edit_mode = None
	obj_mode = False
	stat = "Stat Info"
	screen_x = 64
	vertmode = "Distance"
	area = "N/A"
	auto_update = True
	sel_upd = False

	def modal(self, context, event):
		if event.type in {'ONE', 'TWO', 'THREE', 'TAB'}:
			sel_check(self, context)
			return {'PASS_THROUGH'}

		elif event.type == 'FOUR':
			sel_check(self, context)
			if not self.obj_mode:
				return {'PASS_THROUGH'}

		if event.type == 'V' and event.value == 'RELEASE':
			if self.vertmode == "Distance":
				self.vertmode = "BBox"
			else:
				self.vertmode = "Distance"
			sel_check(self, context)

		# if event.type == 'U' and event.value == 'RELEASE':
		# 	self.auto_update = not self.auto_update

		if context.area and self.sel_upd:
			if self.auto_update:
				sel_check(self, context)
			elif context.mode == "OBJECT":
				sel_check(self, context)

		if self.lines and context.area and event.type == 'TIMER':
			txt_calc(self, context)
			context.area.tag_redraw()

		if event.alt and event.type == "LEFTMOUSE" or event.type == "MIDDLEMOUSE" or \
				event.alt and event.type == "RIGHTMOUSE" or \
				event.shift and event.type == "MIDDLEMOUSE" or \
				event.ctrl and event.type == "MIDDLEMOUSE":
			return {'PASS_THROUGH'}

		elif event.type in {'SPACE', 'ESC', 'RETURN'}:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			bpy.types.SpaceView3D.draw_handler_remove(self._handle_px, 'WINDOW')
			context.area.tag_redraw()
			wm = context.window_manager
			wm.event_timer_remove(self._timer)
			return {'FINISHED'}

		elif event.type == "LEFTMOUSE" or event.type == "RIGHTMOUSE":
			self.sel_upd = True
			return {'PASS_THROUGH'}

		elif event.shift or event.ctrl or event.alt:
			return {'PASS_THROUGH'}

		elif event.type == 'G':
			bpy.ops.transform.translate('INVOKE_DEFAULT')

		elif event.type == 'R':
			bpy.ops.transform.rotate('INVOKE_DEFAULT')

		elif event.type == 'S':
			bpy.ops.transform.resize('INVOKE_DEFAULT')

		elif event.type in {'X', 'Y', 'Z', '<'}:
			return {'PASS_THROUGH'}

		else:
			self.sel_upd = False

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):

		self.auto_update = bpy.context.scene.kekit.quickmeasure
		bpy.ops.wm.tool_set_by_id(name="builtin.select")

		# Make sure active obj is selected
		active_obj = bpy.context.active_object
		sel_obj = context.selected_editable_objects
		if len(sel_obj) == 0 and active_obj:
			active_obj.select_set(state=True)

		bpy.app.handlers.frame_change_post.clear()
		sel_check(self, context)

		if context.area.type == 'VIEW_3D':

			self.screen_x = int(bpy.context.region.width * .5)

			args = (self, context)
			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_view, args, 'WINDOW', 'POST_VIEW')
			self._handle_px = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
			# context.window_manager.modal_handler_add(self)

			wm = context.window_manager
			self._timer = wm.event_timer_add(time_step=0.01, window=context.window)
			wm.modal_handler_add(self)

			context.area.tag_redraw()

			return {'RUNNING_MODAL'}

		else:
			self.report({'WARNING'}, "View3D not found, cannot run operator")
			print("Cancelled: No suitable viewport found")
			return {'CANCELLED'}

		return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	VIEW3D_OT_ke_quickmeasure,
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
