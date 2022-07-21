import bpy, bpy_extras, gpu, bgl, blf

bl_info = {
	"name": "Multires Subdivision",
	"description": "Facilitate the use of multires subdivision",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}

font_size = 12

# Author Laundmo https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b

def draw_hud_prop(self, name, value, offset=0, decimal=2, active=True, prop_offset=170, hint="", hint_offset=220, shadow=True):
	HUDcolor = (1, 1, 1)
	shadow = (0, 0, 0)

	if active:
		alpha = 1
	else:
		alpha = 0.4

	self.HUD_x = bpy.context.region.width/2 - 50
	self.HUD_y = 20

	scale = bpy.context.preferences.view.ui_scale

	offset = self.offset + int(offset * scale)
	self.offset = offset

	if shadow:
		blf.color(self.font_id, *shadow, alpha * 0.7)
		blf.position(self.font_id, self.HUD_x + int(20 * scale) + 1, self.HUD_y + int(20 * scale) + offset + 1, 0)
		blf.size(self.font_id, int(11 * scale), 72)
		blf.draw(self.font_id, name)

	blf.color(self.font_id, *HUDcolor, alpha)
	blf.position(self.font_id, self.HUD_x + int(20 * scale), self.HUD_y + int(20 * scale) + offset, 0)
	blf.size(self.font_id, int(11 * scale), 72)
	blf.draw(self.font_id, name)




	if type(value) is str:
		if shadow:
			blf.color(self.font_id, *shadow, alpha * 0.7)
			blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y + int(20 * scale) + offset + 1, 0)
			blf.size(self.font_id, int(14 * scale), 72)
			blf.draw(self.font_id, value)

		blf.color(self.font_id, *HUDcolor, alpha)
		blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y + int(20 * scale) + offset, 0)
		blf.size(self.font_id, int(14 * scale), 72)
		blf.draw(self.font_id, value)

	elif type(value) is bool:
		if shadow:
			blf.color(self.font_id, *shadow, alpha * 0.7)
			blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y + int(20 * scale) + offset + 1, 0)
			blf.size(self.font_id, int(14 * scale), 72)
			blf.draw(self.font_id, str(value))

		if value:
			blf.color(self.font_id, 0.5, 1, 0.5, alpha)
		else:
			blf.color(self.font_id, 1, 0.3, 0.3, alpha)

		blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y + int(20 * scale) + offset, 0)
		blf.size(self.font_id, int(14 * scale), 72)
		blf.draw(self.font_id, str(value))

	elif type(value) is int:
		if shadow:
			blf.color(self.font_id, *shadow, alpha * 0.7)
			blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y + int(20 * scale) + offset + 1, 0)
			blf.size(self.font_id, int(20 * scale), 72)
			blf.draw(self.font_id, "%d" % (value))

		blf.color(self.font_id, *HUDcolor, alpha)
		blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y + int(20 * scale) + offset, 0)
		blf.size(self.font_id, int(20 * scale), 72)
		blf.draw(self.font_id, "%d" % (value))

	elif type(value) is float:
		if shadow:
			blf.color(self.font_id, *shadow, alpha * 0.7)
			blf.position(self.font_id, self.HUD_x + int(prop_offset * scale) + 1, self.HUD_y + int(20 * scale) + offset + 1, 0)
			blf.size(self.font_id, int(16 * scale), 72)
			blf.draw(self.font_id, "%.*f" % (decimal, value))

		blf.color(self.font_id, *HUDcolor, alpha)
		blf.position(self.font_id, self.HUD_x + int(prop_offset * scale), self.HUD_y + int(20 * scale) + offset, 0)
		blf.size(self.font_id, int(16 * scale), 72)
		blf.draw(self.font_id, "%.*f" % (decimal, value))

	if hint:
		if shadow:
			blf.color(self.font_id, *shadow, 0.6 * 0.7)
			blf.position(self.font_id, self.HUD_x + int(hint_offset *
						 scale) + 1, self.HUD_y - int(20 * scale) + offset + 1, 0)
			blf.size(self.font_id, int(11 * scale), 72)
			blf.draw(self.font_id, "%s" % (hint))

		blf.color(self.font_id, *HUDcolor, 0.6)
		blf.position(self.font_id, self.HUD_x + int(hint_offset * scale), self.HUD_y + int(20 * scale) + offset, 0)
		blf.size(self.font_id, int(11 * scale), 72)
		blf.draw(self.font_id, "%s" % (hint))

class TILA_multires_subdiv_level(bpy.types.Operator):
	bl_idname = "sculpt.tila_multires_subdiv_level"
	bl_label = "TILA : Multires Set Subdivision Level"
	bl_options = {'REGISTER', 'UNDO'}

	subd : bpy.props.IntProperty(name='subd', default=0)
	mode : bpy.props.EnumProperty(items=[("ABSOLUTE", "Absolute", ""), ("RELATIVE", "Relative", ""), ("MIN", "Minimum", ""), ("MAX", "Maximum", "")])
	force_subd : bpy.props.BoolProperty(name='force_subd', default=False)
	algorithm : bpy.props.EnumProperty(items=[("CATMULL_CLARK", "Catmull Clark", ""), ("SIMPLE", "Simple", ""), ("LINEAR", "Linear", "")])


	multires_modifier = None
	active_object = None
	modifier_name = 'Multires'
	modifier_type = 'MULTIRES'
	compatible_type = ['MESH']
	processing = None

	cancelling = False

	def init_default(self):
		self.cancelling = False
		self.processing = None

	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		if event.type == 'TIMER':
			if self.cancelling:
				self.report({'INFO'}, 'TILA Multires Set Subdivision Level : Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.change_subdivision(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, f'TILA Multires Set Subdivision Level to {self.multires_modifier.levels}')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def offset_subdivision(self):
		if self.multires_modifier.render_levels < self.multires_modifier.sculpt_levels + self.subd:
			if self.force_subd:
				bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name, mode=self.algorithm)
		elif self.multires_modifier.sculpt_levels + self.subd < 0:
			if self.force_subd:
				try:
					bpy.ops.object.multires_unsubdivide(modifier=self.multires_modifier.name)
				except RuntimeError:
					self.report({'INFO'}, 'Tila Multires subdiv : Lowest subdivision level reached')
					return {'CANCELLED'}
		else:
			self.multires_modifier.sculpt_levels = self.multires_modifier.sculpt_levels + self.subd

		self.multires_modifier.levels = self.multires_modifier.levels + self.subd

	def set_subdivision(self):
		if self.multires_modifier.render_levels < self.subd:
			if self.force_subd:
				for l in range(self.subd - self.multires_modifier.render_levels):
					bpy.ops.object.multires_subdivide(modifier=self.multires_modifier.name, mode=self.algorithm)

		self.multires_modifier.sculpt_levels = self.subd
		self.multires_modifier.levels = self.subd

	def change_subdivision(self, context, ob):
		self.multires_modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(self.multires_modifier):
			self.multires_modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			self.multires_modifier = self.multires_modifier[0]


		if self.mode == 'RELATIVE':
			self.offset_subdivision()
		elif self.mode == 'ABSOLUTE':
			self.set_subdivision()
		elif self.mode == 'MIN':
			self.subd = 0
			self.set_subdivision()
		elif self.mode == 'MAX':
			self.subd = self.multires_modifier.render_levels
			self.set_subdivision()

	def invoke(self, context, event):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

class TILA_multires_rebuild_subdiv(bpy.types.Operator):
	bl_idname = "sculpt.tila_multires_rebuild_subdiv"
	bl_label = "TILA : Multires Rebuild Subdivision"
	bl_options = {'REGISTER', 'UNDO'}

	modifier_name = 'Multires'
	modifier_type = 'MULTIRES'
	compatible_type = ['MESH']
	processing = None

	cancelling = False

	def init_default(self):
		self.cancelling = False
		self.processing = None

	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		if event.type == 'TIMER':
			if self.cancelling:
				print('TILA Multires Rebuild : Rebuild Cancelled')
				self.report({'INFO'}, 'TILA Multires Rebuild : Rebuild Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.rebuild(context, self.processing)
				self.processing = None

			else:
				print('TILA Multires Rebuild : Rebuild Complete')
				self.report({'INFO'}, 'TILA Multires Rebuild : Rebuild Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def rebuild(self, context, ob):
		print('Rebuild in progress : {}'.format(ob.name))
		self.report({'INFO'}, 'Rebuild in progress : {}'.format(ob.name))
		bpy.context.view_layer.objects.active = ob
		multires_modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(multires_modifier):
			multires_modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			multires_modifier = multires_modifier[0]

		try:
			bpy.ops.object.multires_rebuild_subdiv(modifier=multires_modifier.name)
		except : pass

		multires_modifier.levels = 0
		multires_modifier.sculpt_levels = 0

	def invoke(self, context, event):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

class TILA_multires_delete_subdiv(bpy.types.Operator):
	bl_idname = "sculpt.tila_multires_delete_subdiv"
	bl_label = "TILA : Multires Delete Subdivision"
	bl_options = {'REGISTER', 'UNDO'}

	delete_target : bpy.props.StringProperty(name='subd', default='HIGHER')

	multires_modifier = None
	active_object = None
	modifier_name = 'Multires'
	modifier_type = 'MULTIRES'
	targets = ['HIGHER', 'LOWER']
	compatible_type = ['MESH']

	def invoke(self, context, event):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		if not len(self.object_to_process) or self.delete_target not in self.targets:
			return {'CANCELLED'}
		
		for o in self.object_to_process:
			self.multires_modifier = [m for m in o.modifiers if m.type == self.modifier_type]

			if not len(self.multires_modifier):
				self.multires_modifier = o.modifiers.new(name=self.modifier_name, type=self.modifier_type)
			else:
				self.multires_modifier = self.multires_modifier.pop()

			if self.delete_target == self.targets[0] and self.multires_modifier.render_levels > 0:
				bpy.ops.object.multires_higher_levels_delete(modifier=self.multires_modifier.name)
			elif self.delete_target == self.targets[1] and self.multires_modifier.levels < self.multires_modifier.render_levels:
				bpy.ops.object.multires_lower_levels_delete(modifier=self.multires_modifier.name)

		return {'FINISHED'}

class TILA_multires_apply_base(bpy.types.Operator):
	bl_idname = "sculpt.tila_multires_apply_base"
	bl_label = "TILA : Multires Apply Base"
	bl_options = {'REGISTER', 'UNDO'}

	multires_modifier = None
	active_object = None
	modifier_name = 'Multires'
	modifier_type = 'MULTIRES'
	compatible_type = ['MESH']

	def invoke(self, context, event):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		if not len(self.object_to_process):
			return {'CANCELLED'}

		for o in self.object_to_process:
			self.multires_modifier = [m for m in o.modifiers if m.type == self.modifier_type]

			if not len(self.multires_modifier):
				self.multires_modifier = o.modifiers.new(name=self.modifier_name, type=self.modifier_type)
			else:
				self.multires_modifier = self.multires_modifier.pop()

			bpy.ops.object.multires_base_apply(modifier=self.multires_modifier.name)

		return {'FINISHED'}


class TILA_multires_project_subdivide(bpy.types.Operator):
	bl_idname = "object.tila_multires_project_subdivide"
	bl_label = "TILA : Multires Apply Base"
	bl_options = {'REGISTER', 'UNDO'}

	pre_subdiv_level: bpy.props.IntProperty(name='Pre Subdivision Level', default=0)
	iter_subdiv_level: bpy.props.IntProperty(name='Iterative Subdivision Level', default=1)
	post_subdiv_level: bpy.props.IntProperty(name='Post Subdivision Level', default=0)

	smooth_strength: bpy.props.FloatProperty(name='Smooth Strength', default=0.5)
	apply_modifier: bpy.props.BoolProperty(name='Apply Modifiers', default=False)
	smooth_iteration: bpy.props.IntProperty(name='Initial Smooth Iteration', default=20)

	compatible_projected_type = ['MESH']
	compatible_target_type = ['MESH', 'CURVE', 'META']

	cancelling = False
	tweak_smooth = False
	tweak_iteration = False

	events = ['MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'A', 'S', 'I']

	def invoke(self, context, event):
		self.selection = bpy.context.selected_objects
		self.pre_subdiv_modifier = None
		self.iter_subdiv_modifiers = []
		self.post_subdiv_modifier = None

		if len(self.selection) != 2:
			self.report({'ERROR'}, 'TILA Project Subdivide : Select Projected first, and Target Second')
			return {'CANCELLED'}

		self.projected = self.selection[1]
		self.target = self.selection[0]

		if self.projected.type not in self. compatible_projected_type:
			self.report({'ERROR'}, f'TILA Project Subdivide : Projected object {self.projected.name} not compatible')
			return {'CANCELLED'}
		
		if self.target.type not in self. compatible_target_type:
			self.report({'ERROR'}, f'TILA Project Subdivide : Target object {self.target.name} not compatible')
			return {'CANCELLED'}

		self.last_mouse_x = event.mouse_x
		self._value_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (), 'WINDOW', 'POST_PIXEL')
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}
	
	def revert_initial_values(self):
		pass
	
	def modal(self, context, event):
		# print(event.value, event.type)
		context.area.tag_redraw()
		if event.type in ['ESC', 'RIGHTMOUSE']:
			self.cancelling = True

		if self.cancelling:
			self.revert_initial_values()
			bpy.types.SpaceView3D.draw_handler_remove(self._value_handler, 'WINDOW')
			self.report({'INFO'}, f'Prtojection Cancelled')
			return {"CANCELLED"}

		if event.type in ['RET', 'NUMPAD_ENTER', 'LEFTMOUSE']:
			self.report({'INFO'}, f'Projection complete')
			bpy.types.SpaceView3D.draw_handler_remove(self._value_handler, 'WINDOW')
			return {"FINISHED"}

		if event.type in self.events:

			if event.type == 'MOUSEMOVE' and event.value == 'NOTHING' and self.tweak_smooth:
				self.smooth_strength = self.adjust_modal_value(event, self.smooth_strength, low_clamp=0, high_clamp=1)
				
			if event.type == 'MOUSEMOVE' and event.value == 'NOTHING' and self.tweak_iteration:
				self.smooth_iteration = self.adjust_modal_value(event, self.smooth_iteration, low_clamp=0)

			elif event.type == 'A' and event.value == "PRESS":
				self.apply_modifier = not self.apply_modifier
			
			elif event.type == 'S' and event.value == "PRESS":
				self.tweak_smooth = not self.tweak_smooth

			elif event.type == 'I' and event.value == "PRESS":
				self.tweak_iteration = not self.tweak_iteration

			elif event.type == 'WHEELUPMOUSE' and event.value == "PRESS":
				if event.ctrl:
					self.pre_subdiv_level += 1
				elif event.shift:
					self.post_subdiv_level += 1
				else:
					self.iter_subdiv_level += 1
			
			elif event.type == 'WHEELDOWNMOUSE' and event.value == "PRESS":
				if event.ctrl:
					if self.pre_subdiv_level > 0 :
						self.pre_subdiv_level -= 1
				elif event.shift:
					if self.post_subdiv_level > 0:
						self.post_subdiv_level -= 1
				else:
					if self.iter_subdiv_level > 0:
						self.iter_subdiv_level -= 1

		try:
			success = self.update_modifiers()

			if not success:
				return {"FINISHED"}

			
		except Exception as e:
			pass

		self.last_mouse_x = event.mouse_x
		
		return {"RUNNING_MODAL"}

	def adjust_modal_value(self, event, value, low_clamp=None, high_clamp=None):
		divisor = 100 if event.shift else 1 if event.ctrl else 10

		delta_x = event.mouse_x - self.last_mouse_x
		delta = delta_x / divisor

		if low_clamp is not None and value + delta < low_clamp:
			value = 0
			return value
		elif high_clamp is not None and value + delta > high_clamp:
			value = 1
			return value
		else:
			value += delta
			return value

	def update_modifiers(self):
		if self.pre_subdiv_level > 0:
			if self.pre_subdiv_modifier is None:
				# remove Iter Subdiv
				if len(self.iter_subdiv_modifiers):
					self.remove_iter_modifiers()

				# remove Post Subdiv
				if self.post_subdiv_modifier is not None:
					self.remove_post_subdiv_modifier()

				# Create Pre Subdiv
				self.pre_subdiv_modifier = self.projected.modifiers.new(type='SUBSURF', name='Pre Subdiv')
				self.pre_subdiv_modifier.show_only_control_edges = False

			# Set Subdiv Levels
			self.pre_subdiv_modifier.levels = self.pre_subdiv_levels = self.pre_subdiv_level

		elif self.pre_subdiv_level == 0 and self.pre_subdiv_modifier is not None:
			self.projected.modifiers.remove(self.pre_subdiv_modifier)
			self.pre_subdiv_modifier = None


		if self.iter_subdiv_level > 0:
			if not len(self.iter_subdiv_modifiers) or len(self.iter_subdiv_modifiers) != self.iter_subdiv_level * 3:
				# remove Iter Subdiv
				if len(self.iter_subdiv_modifiers) != self.iter_subdiv_level * 3:
					self.remove_iter_modifiers()

				# remove Post Subdiv
				if self.post_subdiv_modifier is not None:
					self.remove_post_subdiv_modifier()

				for i in range(self.iter_subdiv_level):
					# Create Subdiv Modifier
					subdiv = self.projected.modifiers.new(type='SUBSURF', name=f'Iter Subdiv {i+1}')
					self.iter_subdiv_modifiers.append(subdiv)

					# Create SkinWrap Modifier
					skinwrap = self.projected.modifiers.new(type='SHRINKWRAP', name=f'Iter SkinWrap {i+1}')
					self.iter_subdiv_modifiers.append(skinwrap)

					if i < self.iter_subdiv_level - 1:
						# Create Smooth Modifier
						smooth = self.projected.modifiers.new(type='CORRECTIVE_SMOOTH', name=f'Iter Smooth {i+1}')
						self.iter_subdiv_modifiers.append(smooth)


			for i,m in enumerate(self.iter_subdiv_modifiers):
				if i%3 == 0:
					m.levels = m.render_levels = 1
					m.show_only_control_edges = False
				if i%3 == 1:
					if i == len(self.iter_subdiv_modifiers) - 1:
						m.wrap_method = 'PROJECT'
						m.use_negative_direction = True
						m.project_limit = 0.001
					else:
						m.wrap_method = 'NEAREST_SURFACEPOINT'
					m.target = self.target
				if i < len(self.iter_subdiv_modifiers) - 1:
					if i%3 == 2:
						m.factor = self.smooth_strength
						m.iterations = int(lerp(0, self.smooth_iteration, ((i+1)/3)/(self.iter_subdiv_level-1)))
						m.smooth_type = 'LENGTH_WEIGHTED'
						m.use_only_smooth = True
						m.use_pin_boundary = True

		if self.post_subdiv_level > 0:
			if self.post_subdiv_modifier is None:
				self.post_subdiv_modifier = self.projected.modifiers.new(type='SUBSURF', name='Post Subdiv')
				self.post_subdiv_modifier.show_only_control_edges = False

			self.post_subdiv_modifier.levels = self.post_subdiv_level.render_levels = self.post_subdiv_level

		elif self.post_subdiv_level == 0 and self.post_subdiv_modifier is not None:
			self.projected.modifiers.remove(self.post_subdiv_modifier)
			self.post_subdiv_modifier = None

		return True
	
	def remove_iter_modifiers(self):
		for m in self.iter_subdiv_modifiers:
			self.projected.modifiers.remove(m)
		self.iter_subdiv_modifiers = []

	def remove_post_subdiv_modifier(self):
		self.projected.modifiers.remove(self.post_subdiv_modifier)
		self.post_subdiv_modifier = None

	def draw_HUD(self):
		self.font_id = 0
		self.offset = 0

		offset = 20

		draw_hud_prop(self, "Apply Modifiers", self.apply_modifier, active=self.apply_modifier, hint="toggle A")
		self.offset += offset

		draw_hud_prop(self, "Smooth Iteration", self.smooth_iteration, active=self.smooth_iteration, hint="move LEFT/RIGHT, toggle I")
		self.offset += offset

		draw_hud_prop(self, "Smooth Strength", self.smooth_strength, active=self.smooth_strength, hint="move LEFT/RIGHT, toggle S")
		self.offset += offset

		draw_hud_prop(self, "Post Subdivision Level", self.post_subdiv_level, active=self.post_subdiv_level, hint="SHIFT scroll UP/DOWN")
		self.offset += offset

		draw_hud_prop(self, "Iterative Subdivision Level", self.iter_subdiv_level, active=self.iter_subdiv_level, hint="scroll UP/DOWN")
		self.offset += offset

		draw_hud_prop(self, "Pre Subdivision Level", self.pre_subdiv_level, active=self.pre_subdiv_level, hint="CTRL scroll UP/DOWN")
		self.offset += offset



classes = (
	TILA_multires_subdiv_level,
	TILA_multires_rebuild_subdiv,
	TILA_multires_delete_subdiv,
	TILA_multires_apply_base,
	TILA_multires_project_subdivide
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()
