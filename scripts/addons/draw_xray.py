# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO
#TODO: On snap obj change - undo wont restore shrink wrap target
#TODO: Bad orthogonal drawing

from mathutils import Vector, geometry
bl_info = {"name": "Draw xray",
		   "description": "Draw xray mesh",
		   "author": "JoseConseco",
		   "version": (2, 8),
		   "blender": (2, 93, 0),
		   "location": "3D View(s) -> Top Bar -> View port overlays",
		   "warning": "",
		   "wiki_url": "",
		   "tracker_url": "",
		   "category": "3D View"
		   }

import bpy
import bpy_extras
import bgl
import bmesh
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from bpy.app.handlers import persistent

import numpy as np
#DONE: fix the ortho - kind of done
#DONE: maybe apply shrink wrap as eval mesh-  verts co?
#WONTDO: in multi edited meshes
#DONE: snap to target/offset as bpy.types.Obj property - remake snappint for that
#DONE: custom highlight color
#DOTO: if goin to obj mode -apply mod
#DONE: fix no bmesh, when opening scene. Maybe disable xray on quit/load?
#DONE: fix blinking mirror mod


BATCH_FACE_HIGHLIGHT = None
BATCH_FACES = None
EDGES_BATCH = None
VERTS_BATCH = None
PAUSE_HANDLERS = False #to avoid recursion
CACHED_OPERATOR_ID = ''  # to avoid recursion
FORCE_UPDATE_XRAY = False
DEPSGRAPH = None  # cache depsgraph for checking for updates handler
# shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

vertex_shader = '''
	uniform mat4 viewProjectionMatrix;
	uniform float bias_z;
	uniform vec3 camPos;

	vec4 outPos;

	in vec3 pos;
	in vec4 col;
	in vec3 nrm;

	out vec4 color;
	out float oDot;
	void main()
	{
		outPos = viewProjectionMatrix * vec4(pos, 1.0f);
		color = col;
		oDot = dot(nrm, normalize(camPos-pos));
		outPos.z = outPos.z - bias_z/outPos.z; // counter w division for shift
		gl_Position = outPos;
	}
'''

fragment_shader = '''
	in vec4 color;
	in float oDot;
	out vec4 fragColor;
	void main()
	{
		vec4 out_color;
		if (oDot>0.0)
		{
			out_color = vec4(color.xyz * (0.3 + 0.7*oDot), color.w);
		}
		else
		{
			out_color = vec4(color.xyz * (0.3 + 0.7*oDot), 0.0);
		}
		fragColor = out_color;
	}
'''

shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
shader3D = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

def draw_callback_xray(self, context):
	active_obj = bpy.context.active_object
	if active_obj is None or not bpy.context.space_data.overlay.show_overlays:
		return

	xray_props = context.scene.xray_props
	obj_xprop = active_obj.xray_props
	if xray_props.draw_xray_mode == 'DISABLED' \
	 or (xray_props.draw_xray_mode == 'PER_OBJ' and not obj_xprop.enable_xray):
		return

	if active_obj.type == 'MESH' and active_obj.mode == 'EDIT' and BATCH_FACES:
		theme = bpy.context.preferences.themes['Default']
		g_vertex_size = theme.view_3d.vertex_size

		highlight_color = xray_props.highlight_color

		bgl.glEnable(bgl.GL_BLEND)
		bgl.glLineWidth(1)
		bgl.glPointSize(g_vertex_size + 1)
		bgl.glEnable(bgl.GL_CULL_FACE)
		bgl.glCullFace(bgl.GL_BACK)
		is_perspective = bpy.context.region_data.is_perspective
		if is_perspective:
			bgl.glEnable(bgl.GL_DEPTH_TEST)
		else: #hack cos I duno how fix bias in ortho
			bgl.glDisable(bgl.GL_DEPTH_TEST)

		# bgl.glPolygonMode(bgl.GL_FRONT_AND_BACK, bgl.GL_LINE)
		# bgl.glDepthRange(0, 1 -  offset_depth)
		# bgl.glEnable(bgl.GL_POLYGON_OFFSET_FILL)
		# bgl.glPolygonOffset(xray_props.drawOffset, 0.01)

		if is_perspective:
			camera_pos = bpy.context.region_data.view_matrix.inverted().translation
			offset = xray_props.drawOffset/50
		else:
			# cam_dir_z = Vector((view_mat[2][0], view_mat[2][1], view_mat[2][2]))
			qat = context.region_data.view_rotation
			cam_dir_z = qat @ Vector((0, 0, 1))  # rotate Z vector by quat
			camera_pos = cam_dir_z * 100
			offset = 0.0
		matrix = context.region_data.perspective_matrix

		shader.bind()
		shader.uniform_float("viewProjectionMatrix", matrix)
		shader.uniform_float("bias_z", offset)
		shader.uniform_float("camPos", camera_pos)

		# http://glprogramming.com/red/chapter14.html#name16
		#* Fix dem ugly lines width that vary randomly.... Cos lines are drawn as thin polys. And depth buffer BATCH_FACES messes them up
		bgl.glPolygonMode(bgl.GL_FRONT_AND_BACK, bgl.GL_FILL)
		bgl.glEnable(bgl.GL_POLYGON_OFFSET_FILL)
		bgl.glPolygonOffset(1.0, 1.0)
		BATCH_FACES.draw(shader)

		bgl.glPolygonMode(bgl.GL_FRONT_AND_BACK, bgl.GL_LINE) #?
		EDGES_BATCH.draw(shader)
		if bpy.context.tool_settings.mesh_select_mode[0]:
			VERTS_BATCH.draw(shader)
		# restore opengl defaults

		bgl.glPolygonMode(bgl.GL_FRONT_AND_BACK, bgl.GL_FILL) #? defalt
		bgl.glDisable(bgl.GL_POLYGON_OFFSET_FILL)
		# bgl.glDepthRange(0, 1)
		bgl.glDisable(bgl.GL_DEPTH_TEST)
		bgl.glDisable(bgl.GL_CULL_FACE)
		# bgl.glPolygonMode(bgl.GL_FRONT_AND_BACK, bgl.GL_FILL)
		bgl.glLineWidth(1)
		bgl.glPointSize(1)
		bgl.glDisable(bgl.GL_BLEND)

		# Selection Highlight
		bgl.glEnable(bgl.GL_LINE_SMOOTH)
		# bgl.glDepthFunc(bgl.GL_ALWAYS)
		bgl.glEnable(bgl.GL_BLEND)
		# bgl.glEnable(bgl.GL_DEPTH_TEST)
		# bgl.glDepthMask(bgl.GL_FALSE)
		bgl.glEnable(bgl.GL_CULL_FACE)

		shader3D.bind()
		shader3D.uniform_float("color", highlight_color)

		for b in BATCH_FACE_HIGHLIGHT:
			b.draw(shader3D)

		# bgl.glDisable(bgl.GL_DEPTH_TEST)
		bgl.glDisable(bgl.GL_BLEND)
		# bgl.glDepthMask(bgl.GL_FALSE)
		bgl.glDisable(bgl.GL_CULL_FACE)



class ScnDrawXrayProps(bpy.types.PropertyGroup):
	def DrawXrayUpdate(self,context):
		if context.active_object and \
			(self.draw_xray_mode == 'DISABLED' \
			or (self.draw_xray_mode == 'ENABLED' and not context.scene.xray_props.enable_snapping)
			or (self.draw_xray_mode == 'PER_OBJ' and not context.active_object.xray_props.enable_snapping)):
			apply_shrink_final()
		handle_handlers_draw_xray()
		refresh_draw_buffers()
		if context.active_object and context.active_object.type == 'MESH':
			context.active_object.data.update_tag()

	def refresh_buff(self,context):
		refresh_draw_buffers()
		context.active_object.data.update_tag()


	def toggle_snapping(self,context):
		if self.snap_target and self.snap_target.type != 'MESH':
			self['snap_target'] = None
		if not self.enable_snapping:
			self['enable_snapping'] = False #?
			apply_shrink_final(all_objs = True)
		global FORCE_UPDATE_XRAY
		FORCE_UPDATE_XRAY = True
		check_obj_updated()
		context.active_object.data.update_tag()

	draw_xray_mode: bpy.props.EnumProperty(name='X-ray', description="Draws current mesh on top of retopo mesh",
											  items=[
												   ('DISABLED', 'Disabled', 'Disable object snapping for all objects'),
												  ('ENABLED', 'Enabled', "Enable Xray Globally for any selected object"),
												  ('PER_OBJ', 'Per Object Settings', 'Enable/Disable snapping, with individual settings, per each object')
											  ], default='ENABLED', update=DrawXrayUpdate)

	drawOffset: bpy.props.FloatProperty(name="Depth Bias", description="Moves rendering of mesh closer to camera (does not affect mesh geometry)",
										min=0.0001, soft_max=1.0, default=0.2, subtype='FACTOR', update=refresh_buff)
	polygon_opacity: bpy.props.FloatProperty(name="Face opacity", description="Face opacity", min=0.0, max=1.0, default=0.5, subtype='PERCENTAGE', update=refresh_buff)
	edge_opacity: bpy.props.FloatProperty(name="Edge opacity", description="Edge opacity", min=0.0, max=1.0, default=0.5, subtype='PERCENTAGE', update=refresh_buff)
	face_color:  bpy.props.FloatVectorProperty(name="Face Color", subtype='COLOR', size=4, default=(0.1, 0.8, 0.0, 0.5), min=0.0, max=1.0, description="color picker", update=refresh_buff)
	highlight_color:  bpy.props.FloatVectorProperty(name="Highlight Color", subtype='COLOR', size = 4, default=(1.0, 0.8, 0.0, 0.5), min=0.0, max=1.0, description="color picker", update=refresh_buff)

	draw_modifiers: bpy.props.BoolProperty(name="Draw Modifiers", description="Draws retopo mesh with modifiers", default=True, update=refresh_buff)
	enable_snapping: bpy.props.BoolProperty(name="Enable snapping", description="Enable global snapping, for all objects on scene", default=False, update=toggle_snapping)
	snap_offset: bpy.props.FloatProperty( name="Snap offset", description="Offset retopo mesh vertices above high-poly mesh surface.", default=0.01, soft_min=0.0, soft_max=0.1, update=toggle_snapping)
	snap_target: bpy.props.PointerProperty(name='Snap Target', description="Default snap target object for all objects.", type=bpy.types.Object, update=toggle_snapping)

	wrap_method: bpy.props.EnumProperty(name="Mode", description="Shrink wrap Mode", default="NEAREST_SURFACEPOINT",
											  items=[('NEAREST_SURFACEPOINT', 'Nearest Surface point', ''),
													 ('PROJECT', 'Project', ''),
													 ('NEAREST_VERTEX', 'Nearest Vertex', ''),
													 ('TARGET_PROJECT', 'Target Normal Project', '')
													 ], update=toggle_snapping)
	wrap_mode: bpy.props.EnumProperty(name='Wrap Mode', description='Wrap Mode',
		items=[('ON_SURFACE', 'On Surface', 'On Surface'),
			('INSIDE', 'Inside', 'Inside'),
			('OUTSIDE', 'Outside', 'Outside'),
			('OUTSIDE_SURFACE', 'Outside Surface', 'Outside Surface'),
			('ABOVE_SURFACE', 'Above surface', 'Above_surface')],
		default='OUTSIDE_SURFACE', update=toggle_snapping)


class ObjDrawXrayProps(bpy.types.PropertyGroup):
	def toggle_snapping(self, context):
		if self.snap_target and (self.snap_target.type != 'MESH' or self.snap_target == context.active_object):
			self['snap_target'] = None

		global FORCE_UPDATE_XRAY
		FORCE_UPDATE_XRAY = True
		check_obj_updated()
		context.active_object.data.update_tag()

	def refresh_buff(self, context):
		refresh_draw_buffers()
		context.active_object.data.update_tag()

	enable_xray: bpy.props.BoolProperty(name='Draw Overlay', default=True)
	draw_modifiers: bpy.props.BoolProperty(name="Draw Modifiers", description="Draws retopo mesh with modifiers", default=True, update=refresh_buff)
	enable_snapping: bpy.props.BoolProperty(name="Enable snapping", description="Enable global snapping, for all objects on scene", default=False, update=toggle_snapping)
	snap_offset: bpy.props.FloatProperty( name="Snap offset", description="Offset retopo mesh vertices above high-poly mesh surface", default=0.01, soft_min=0.0, soft_max=0.1, update=toggle_snapping)
	snap_target: bpy.props.PointerProperty(name='Snap Target', description="Snap target mesh", type=bpy.types.Object, update=toggle_snapping)

	wrap_method: bpy.props.EnumProperty(name="Mode", description="Shrink wrap Mode", default="NEAREST_SURFACEPOINT",
										items=[('NEAREST_SURFACEPOINT', 'Nearest Surface point', ''),
											   ('PROJECT', 'Project', ''),
											   ('NEAREST_VERTEX', 'Nearest Vertex', ''),
											   ('TARGET_PROJECT', 'Target Normal Project', '')
											   ])
	wrap_mode: bpy.props.EnumProperty(name='Wrap Mode', description='Wrap Mode',
									  items=[('ON_SURFACE', 'On Surface', 'On Surface'),
											 ('INSIDE', 'Inside', 'Inside'),
											 ('OUTSIDE', 'Outside', 'Outside'),
											 ('OUTSIDE_SURFACE', 'Outside Surface', 'Outside Surface'),
											 ('ABOVE_SURFACE', 'Above surface', 'Above_surface')],
									  default='ABOVE_SURFACE')



def ShadingXrayPanel(self, context):
	if context.active_object and context.active_object.type == 'MESH':
		xray_props = context.scene.xray_props
		obj_xprop = context.active_object.xray_props

		box = self.layout.box()
		main_col = box.column()
		if xray_props.draw_xray_mode in {'DISABLED', 'PER_OBJ'}:
			main_col.prop(xray_props, "draw_xray_mode")
		if xray_props.draw_xray_mode == 'ENABLED':
			row = main_col.row(align=True)
			row.prop(xray_props, "draw_xray_mode")
			row.prop(xray_props, "draw_modifiers", icon="MODIFIER", icon_only = True)


		if xray_props.draw_xray_mode != 'DISABLED':
			#* Overlay Drawing  Settings
			sub_box = main_col.box()
			sub_col = sub_box.column()
			if xray_props.draw_xray_mode == 'PER_OBJ':
				row = sub_col.row(align=True)
				row.prop(obj_xprop, "enable_xray", icon='MOD_SOLIDIFY')
				row.prop(obj_xprop, "draw_modifiers", icon="MODIFIER", icon_only=True)

			if xray_props.draw_xray_mode == 'ENABLED' or (xray_props.draw_xray_mode == 'PER_OBJ' and obj_xprop.enable_xray):
				if xray_props.draw_xray_mode == 'ENABLED':
					sub_col.label(text='Overlay settings')
				row = sub_col.row(align=True)
				row.prop(xray_props, "drawOffset")
				row = sub_col.row(align=True)
				row.prop(xray_props, "polygon_opacity")
				row.prop(xray_props, "edge_opacity")
				row = sub_col.row(align=True)
				row.label(text="Faces color")
				row.prop(xray_props, "face_color", text='')
				row = sub_col.row(align=True)
				row.label(text="Highlight color")
				row.prop(xray_props, "highlight_color", text='')
			if xray_props.draw_xray_mode == 'ENABLED':
				sub_box = main_col.box()
				sub_col = sub_box.column()
				sub_box.enabled = False
				sub_col.prop(xray_props, "enable_snapping", icon='SNAP_ON' if xray_props.enable_snapping else 'SNAP_OFF', text = 'Enable snapping (only in paid version)')

			elif xray_props.draw_xray_mode == 'PER_OBJ':
				sub_box = main_col.box()
				sub_box.enabled = False
				sub_col = sub_box.column()
				sub_col.prop(obj_xprop, "enable_snapping", icon='SNAP_ON' if obj_xprop.enable_snapping else 'SNAP_OFF', text = 'Enable snapping (only in paid version)')




class XRAY_OT_ObjectPicker(bpy.types.Operator):
	bl_idname = "xray.object_picker"
	bl_label = "Pick Object"
	bl_description = 'Pick Object under the cursor'
	bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

	use_scn_prop: bpy.props.BoolProperty(name='Scene prop', description='Pick scn.snap_target prop or obj.snap_target', default=True)

	@classmethod
	def poll(cls, context):
		return True

	def invoke(self, context, event):
		self.lmb_clicked = True
		self.obj = None
		context.window.cursor_modal_set('EYEDROPPER')
		context.window_manager.modal_handler_add(self)
		self.depsgraph = context.evaluated_depsgraph_get()
		return {"RUNNING_MODAL"}

	def scn_ray_cast(self, context, event):
		''' using scn.ray_cast '''
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
		# hit, loc, norm, idx, obj, mat = context.scene.ray_cast(context.view_layer, ray_origin, view_vector, distance=1.0e+6) #old
		hit, loc, norm, idx, obj, mat = context.scene.ray_cast(self.depsgraph, ray_origin, view_vector, distance=1.0e+6)
		return obj

	def modal(self, context, event):
		if event.type == 'MOUSEMOVE':
			self.obj = self.scn_ray_cast(context, event)
			context.area.header_text_set(self.obj.name if self.obj else None)

		elif event.type == "MIDDLEMOUSE":
			return {'PASS_THROUGH'}

		elif event.type == "LEFTMOUSE":
			if self.obj and self.obj.type == 'MESH':
				if self.use_scn_prop:
					context.scene.xray_props.snap_target = self.obj
				else:
					context.active_object.xray_props.snap_target = self.obj
				self.report({'INFO'}, f'Picked {self.obj.name}')
			else:
				self.report({'WARNING'}, 'Pick mesh type of object')
			context.window.cursor_modal_restore()
			context.area.header_text_set(None)
			return {"FINISHED"}

		elif event.type in {"RIGHTMOUSE", "ESC"}:
			context.window.cursor_modal_restore()
			context.area.header_text_set(None)
			return {"CANCELLED"}

		return {"RUNNING_MODAL"}


handle_SpaceView3D = None

@persistent
def xray_scene_update(scene):
	global DEPSGRAPH
	DEPSGRAPH = bpy.context.evaluated_depsgraph_get()
	if PAUSE_HANDLERS:
		return
	check_obj_updated()


@persistent
def depsgraph_update(scene):
	global DEPSGRAPH
	DEPSGRAPH = bpy.context.evaluated_depsgraph_get()
	#DO I NEED IT?
	handle_handlers_draw_xray() #! disable if needed eg. on undo
	check_obj_updated()

@persistent
def DrawXrayPost(scn):
	handle_handlers_draw_xray()

@persistent
def DrawXrayLoadDisable(scn):
	#print('Disabling xray on load handerl')
	global DEPSGRAPH
	DEPSGRAPH = bpy.context.evaluated_depsgraph_get()
	bpy.context.scene.xray_props['enable_snapping'] = False  #
	bpy.context.scene.xray_props.draw_xray_mode = 'DISABLED'  # to avoid bm edit error


def handle_handlers_draw_xray():
	global handle_SpaceView3D
	xray_props = bpy.context.scene.xray_props
	if xray_props.draw_xray_mode != 'DISABLED':
		if handle_SpaceView3D is None:
			args = (ScnDrawXrayProps, bpy.context)  # u can pass arbitrary class as first param  Instead of (self, context)
			handle_SpaceView3D = bpy.types.SpaceView3D.draw_handler_add(draw_callback_xray, args, 'WINDOW', 'POST_VIEW')

		if xray_scene_update not in bpy.app.handlers.depsgraph_update_post:
			bpy.app.handlers.depsgraph_update_post.append(xray_scene_update)
		if depsgraph_update not in bpy.app.handlers.undo_post:
			bpy.app.handlers.undo_post.append(depsgraph_update)

		if depsgraph_update not in bpy.app.handlers.redo_post:
			bpy.app.handlers.redo_post.append(depsgraph_update)
	else:
		if handle_SpaceView3D is not None:
			bpy.types.SpaceView3D.draw_handler_remove(handle_SpaceView3D, 'WINDOW')
			handle_SpaceView3D = None

		if xray_scene_update in bpy.app.handlers.depsgraph_update_post:
			bpy.app.handlers.depsgraph_update_post.remove(xray_scene_update)

		if depsgraph_update in bpy.app.handlers.undo_post:
			bpy.app.handlers.undo_post.remove(depsgraph_update)

		if depsgraph_update in bpy.app.handlers.redo_post:
			bpy.app.handlers.redo_post.remove(depsgraph_update)


def shrink_transfer(active_obj):
	#transfer 'shrink_xray' mod to bm verts
	disabled_mods = []
	# print('Disabling mods')
	for mod in active_obj.modifiers:
		if mod.name != 'shrink_xray' and mod.show_viewport:
			mod.show_viewport = False
			disabled_mods.append(mod)

	# depsgraph = bpy.context.evaluated_depsgraph_get() #to force addon to see disabled mods
	depsgraph = DEPSGRAPH
	depsgraph.update() #to get disabled mods
	obj_eval = active_obj.evaluated_get(depsgraph)
	mesh_with_mod = obj_eval.to_mesh()

	if active_obj.mode == 'EDIT': #when adding geo, use bm, to get updated vertcount
		bm = bmesh.from_edit_mesh(active_obj.data)
		edit_v_count = len(bm.verts)
	else:
		edit_v_count = len(active_obj.data.vertices)

	if len(mesh_with_mod.vertices) != edit_v_count:
		#print(f'Eval mesh has different vert count. Eval count is: {len(mesh_with_mod.vertices)},  mesh coutn is: {edit_v_count}')
		obj_eval.to_mesh_clear()
		# print('enabling mods')
		for mod in disabled_mods:
			mod.show_viewport = True
		return

	#shrink wrap moves center verts slightly off center. Deal with it below
	mirror_mod = [mod for mod in active_obj.modifiers if mod.type == 'MIRROR' and mod.mirror_object == None and mod.use_axis[0]]
	if active_obj.mode == 'EDIT':
		bm = bmesh.from_edit_mesh(active_obj.data)
		if mirror_mod:
			for b_vert, eval_v in zip(bm.verts, mesh_with_mod.vertices):
				b_vert.co = eval_v.co
				if abs(eval_v.co.x) < 2*mirror_mod[0].merge_threshold: #snap to center
					b_vert.co.x = 0
		else:
			for b_vert, eval_v in zip(bm.verts, mesh_with_mod.vertices):
				b_vert.co = eval_v.co
		bmesh.update_edit_mesh(active_obj.data)
	elif active_obj.mode == 'SCULPT':
		mod_verts_np = np.empty((len(active_obj.data.vertices), 3), 'f')
		mesh_with_mod.vertices.foreach_get("co", np.reshape(mod_verts_np, len(mesh_with_mod.vertices) * 3))
		if mirror_mod:
			mod = mirror_mod[0]
			mod_verts_np[np.abs(mod_verts_np[:, 0]) < 2*mod.merge_threshold, 0] = 0
		active_obj.data.vertices.foreach_set('co', mod_verts_np.ravel())
		active_obj.data.update()

	obj_eval.to_mesh_clear()
	# print('enabling mods')
	for mod in disabled_mods:
		mod.show_viewport = True

def refresh_draw_buffers():
	xray_props = bpy.context.scene.xray_props
	active_obj = bpy.context.active_object
	if not active_obj:
		return
	obj_xprop = active_obj.xray_props
	if xray_props.draw_xray_mode == 'DISABLED' or (xray_props.draw_xray_mode == 'PER_OBJECT' and not obj_xprop.enable_xray):
		return
	active_obj.update_from_editmode() #to get correct highlights
	# depsgraph = bpy.context.evaluated_depsgraph_get() #somehow using DEPSGRAPH here, causes blink of modifiers
	depsgraph = DEPSGRAPH
	if not depsgraph:
		return

	draw_mods = (xray_props.draw_xray_mode == 'ENABLED' and xray_props.draw_modifiers) or \
				(xray_props.draw_xray_mode == 'PER_OBJ' and obj_xprop.enable_xray and obj_xprop.draw_modifiers)
	if len(active_obj.modifiers) > 0:  # Polyquilt  fix but wont work - selection not updated if no modifiers, and  draw_modifiers == True
		depsgraph.update()  # to get disabled mods/ update selection higlight if draw mods_on,
		if len(active_obj.modifiers) > 0 and draw_mods:
			obj_eval = active_obj.evaluated_get(depsgraph)
			mesh = obj_eval.to_mesh()
		else:
			mesh = active_obj.data
	else:
		mesh = active_obj.data

	theme = bpy.context.preferences.themes['Default']

	g_vertex_color = theme.view_3d.vertex
	g_vertex_size = theme.view_3d.vertex_size
	g_wire_edit_color = theme.view_3d.wire_edit

	g_face_color = xray_props.face_color
	highlight_color = xray_props.highlight_color
	#print('Runinig buffer update')
	mesh.calc_loop_triangles()
	vert_count = len(mesh.vertices)
	VERTICES = np.empty((vert_count, 3), 'f')
	INDICES = np.empty((len(mesh.loop_triangles), 3), 'i')
	NORMALS = np.empty((vert_count, 3), 'f')
	mesh.transform(active_obj.matrix_world)
	mesh.update()  #? recalc normals
	mesh.vertices.foreach_get("co", np.reshape(VERTICES, vert_count * 3))
	mesh.vertices.foreach_get("normal", np.reshape(NORMALS, vert_count * 3))
	mesh.loop_triangles.foreach_get("vertices", np.reshape(INDICES, len(mesh.loop_triangles) * 3))

	face_col = [(g_face_color[0], g_face_color[1], g_face_color[2], g_face_color[3] * xray_props.polygon_opacity/2) for _ in range(vert_count)]
	edge_col = [(g_wire_edit_color.r, g_wire_edit_color.g, g_wire_edit_color.b, xray_props.edge_opacity*0.7) for _ in range(vert_count)]
	
	vert_opacity = min(xray_props.edge_opacity+0.2, 1.0)
	vert_col = [(g_vertex_color.r, g_vertex_color.g, g_vertex_color.b, vert_opacity) for _ in range(vert_count)]
	for i,vert in enumerate(mesh.vertices):
		if vert.select:
			# edge_col[i] = (highlight_color[0], highlight_color[1], highlight_color[2], xray_props.edge_opacity*0.7)é
			vert_col[i] = (highlight_color[0], highlight_color[1], highlight_color[2], vert_opacity)
			# face_col[i] = (highlight_color[0], highlight_color[1], highlight_color[2], highlight_color[3] * xray_props.polygon_opacity/2)

   
	global BATCH_FACES, EDGES_BATCH, VERTS_BATCH


	global BATCH_FACE_HIGHLIGHT
	BATCH_FACE_HIGHLIGHT = []
	bm = bmesh.from_edit_mesh(active_obj.data)
	drawElementsHilight3D(active_obj, elements=[e for e in bm.faces if e.select])
	drawElementsHilight3D(active_obj, elements=[e for e in bm.edges if e.select], isFill=False)
	bmesh.update_edit_mesh(mesh=active_obj.data, loop_triangles=True)

	BATCH_FACES = batch_for_shader(shader, 'TRIS', {"pos": VERTICES, "col": face_col, 'nrm': NORMALS}, indices=INDICES,)
	EDGES_BATCH = batch_for_shader(shader, 'LINES', {"pos": VERTICES, "col": edge_col, 'nrm': NORMALS}, indices=mesh.edge_keys)
	VERTS_BATCH = batch_for_shader(shader, 'POINTS', {"pos": VERTICES, "col": vert_col, 'nrm': NORMALS})

	
	if draw_mods and len(active_obj.modifiers) > 0:
		obj_eval.to_mesh_clear()
	else:
		mesh.transform(active_obj.matrix_world.inverted())

PREV_MODE = 'OBJECT' #helper for applying shrink wrap, when going  obj mode
def check_obj_updated():
	active_obj = bpy.context.active_object
	if not active_obj:
		return
	global PAUSE_HANDLERS, PREV_MODE, FORCE_UPDATE_XRAY
	if PAUSE_HANDLERS:
		return
	PAUSE_HANDLERS = True
	xray_props = bpy.context.scene.xray_props
	obj_xray_props = active_obj.xray_props

	if xray_props.draw_xray_mode != 'DISABLED':
		active_obj = bpy.context.active_object
		if active_obj.mode == 'OBJECT' and PREV_MODE == 'EDIT':
			apply_shrink_final()
		PREV_MODE = active_obj.mode
		if active_obj and active_obj.type == 'MESH' and active_obj.mode in ('EDIT', 'SCULPT'):
			depsgraph = DEPSGRAPH
			if FORCE_UPDATE_XRAY:
				write_shrink_mod()
				refresh_draw_buffers()
				FORCE_UPDATE_XRAY = False
				PAUSE_HANDLERS = False
				return

			if hasattr(depsgraph, 'updates'):
				for update in depsgraph.updates:
					#print((f'ID {update.id}, geom {update.is_updated_geometry}, xform {update.is_updated_transform}'))
					if update.id.name == active_obj.name and (update.is_updated_geometry or update.is_updated_transform or update.id.is_evaluated):
						write_shrink_mod()
						refresh_draw_buffers()
						PAUSE_HANDLERS = False
						return
	PAUSE_HANDLERS = False

def apply_shrink_final():
	obj = bpy.context.active_object
	if not obj or obj.type != 'MESH':
		return
	snap_mod = [mod for mod in obj.modifiers if mod.name == 'shrink_xray']
	if snap_mod:
		back_mode = obj.mode
		if obj.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.modifier_apply(modifier=snap_mod[0].name)
		if back_mode != 'OBJECT':
			bpy.ops.object.mode_set(mode=back_mode)


def write_shrink_mod():
	# Determine if the modifier needs to be applied.
	xray_props = bpy.context.scene.xray_props

	active_object = bpy.context.active_object
	obj_xray_props = active_object.xray_props
	if xray_props.draw_xray_mode == 'DISABLED' or \
		(xray_props.draw_xray_mode == 'ENABLED' and not xray_props.enable_snapping)  \
		or (xray_props.draw_xray_mode == 'PER_OBJ' and not obj_xray_props.enable_snapping):
		apply_shrink_final()  # if exist apply shrink
		return
	current_oper = hash(bpy.context.active_operator)
	global CACHED_OPERATOR_ID
	#print(f'Currrent oper: {current_oper}')
	#print(f'cached oper as id: {CACHED_OPERATOR_ID}')
	if (current_oper and current_oper != CACHED_OPERATOR_ID) or FORCE_UPDATE_XRAY:
		CACHED_OPERATOR_ID = current_oper
		#print('write shrink mod to mesh')
		target = None
		if xray_props.draw_xray_mode == 'ENABLED':  # use global snapping is local snapping is disabbled
			if xray_props.snap_target and xray_props.snap_target.name in bpy.context.scene.objects.keys() and xray_props.snap_target.name != active_object.name:
				target = xray_props.snap_target
				offset = xray_props.snap_offset
				wrap_mode = xray_props.wrap_mode
				wrap_method = xray_props.wrap_method

		elif xray_props.draw_xray_mode == 'PER_OBJ':
			# use local obj snapping first if exist
			if obj_xray_props.snap_target and obj_xray_props.snap_target.name in bpy.context.scene.objects.keys() and obj_xray_props.snap_target.name != active_object.name:
				target = obj_xray_props.snap_target
				offset = obj_xray_props.snap_offset
				wrap_mode = obj_xray_props.wrap_mode
				wrap_method = obj_xray_props.wrap_method

		if not target:  # no snapping was defined so just skip
			apply_shrink_final()  # if exist apply shrink
			return

		snap_mod = [mod for mod in active_object.modifiers if mod.name == 'shrink_xray']
		if not snap_mod:
			wrap_method = wrap_method
			modifier = active_object.modifiers.new(name="shrink_xray", type='SHRINKWRAP')
			modifier.show_expanded = False
			modifier.show_viewport = True
			modifier.show_in_editmode = True
			modifier.show_on_cage = True
			modifier.use_negative_direction = True
			modifier.wrap_method = wrap_method
			modifier.wrap_mode = wrap_mode
			modifier.use_negative_direction = True
			modifier.use_positive_direction = True

			while active_object.modifiers[0] != modifier:
				bpy.ops.object.modifier_move_up(modifier=modifier.name)
		else:
			modifier = snap_mod[0]
		if target != modifier.target:
			modifier.target = target
		if offset != modifier.offset:
			modifier.offset = offset

		shrink_transfer(active_object) #below will crash so this
		# modifier_apply - crashes it seems
		# back_mode = active_object.mode
		# bpy.ops.object.mode_set(mode='OBJECT')
		# bpy.ops.object.modifier_apply(modifier=modifier.name)
		# bpy.ops.object.mode_set(mode=back_mode)
		# global DEPSGRAPH
		# DEPSGRAPH = bpy.context.evaluated_depsgraph_get()
		# refresh_draw_buffers()


def drawElementsHilight3D(obj, elements, isFill=True):
	if isFill:
		for e in elements:
			vs = [obj.matrix_world @ v.vert.co for v in e.loops]
			polys = geometry.tessellate_polygon((vs,))

			# batch_draw(shader3D, 'TRIS', {"pos": vs}, indices=polys)
			BATCH_FACE_HIGHLIGHT.append(batch_for_shader(shader3D, 'TRIS', {"pos": vs}, indices=polys))
	else:
		verts = []
		edges = []
		for e in elements:
			if e not in edges:
				verts.append(obj.matrix_world @ e.verts[0].co)
				verts.append(obj.matrix_world @ e.verts[1].co)

		BATCH_FACE_HIGHLIGHT.append(batch_for_shader(shader3D, 'LINES', {"pos": verts}))


def register():
	bpy.utils.register_class(ScnDrawXrayProps)
	bpy.utils.register_class(XRAY_OT_ObjectPicker)
	bpy.utils.register_class(ObjDrawXrayProps)
	bpy.types.Scene.xray_props = bpy.props.PointerProperty(type=ScnDrawXrayProps)
	bpy.types.Object.xray_props = bpy.props.PointerProperty(type=ObjDrawXrayProps)
	bpy.types.VIEW3D_PT_overlay.append(ShadingXrayPanel)
	bpy.app.handlers.load_post.append(DrawXrayLoadDisable)


def unregister():
	global handle_SpaceView3D
	bpy.types.VIEW3D_PT_overlay.remove(ShadingXrayPanel)
	if handle_SpaceView3D is not None:
		bpy.types.SpaceView3D.draw_handler_remove(handle_SpaceView3D, 'WINDOW')
		handle_SpaceView3D = None

	if xray_scene_update in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.remove(xray_scene_update)

	if depsgraph_update in bpy.app.handlers.undo_post:
		bpy.app.handlers.undo_post.remove(depsgraph_update)
	if depsgraph_update in bpy.app.handlers.redo_post:
		bpy.app.handlers.redo_post.remove(depsgraph_update)

	bpy.app.handlers.load_post.remove(DrawXrayLoadDisable)

	#line below trigger prop.update=DrawXrayUpdate from xray_props property group
	bpy.context.scene.xray_props.draw_xray_mode = 'DISABLED'  #! TO hide draw xray on F8 reload - place alway after removing halders (or crash)
	del bpy.types.Scene.xray_props
	del bpy.types.Object.xray_props
	bpy.utils.unregister_class(ScnDrawXrayProps)
	bpy.utils.unregister_class(XRAY_OT_ObjectPicker)
	bpy.utils.unregister_class(ObjDrawXrayProps)


if __name__ == "__main__":
	register()
