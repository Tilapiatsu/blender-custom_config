import bpy

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
				self.report({'INFO'}, 'TILA Multires Set Subdivision Level : Complete')
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
				self.report({'INFO'}, 'TILA Multires Rebuild : Rebuild Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.rebuild(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, 'TILA Multires Rebuild : Rebuild Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def rebuild(self, context, ob):
		self.report({'INFO'}, 'Rebuild in progress : {}'.format(ob.name))
		bpy.context.view_layer.objects.active = ob
		multires_modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(multires_modifier):
			multires_modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			multires_modifier = multires_modifier[0]

		bpy.ops.object.multires_rebuild_subdiv(modifier=multires_modifier.name)

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


classes = (
	TILA_multires_subdiv_level,
	TILA_multires_rebuild_subdiv,
	TILA_multires_delete_subdiv,
	TILA_multires_apply_base
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()