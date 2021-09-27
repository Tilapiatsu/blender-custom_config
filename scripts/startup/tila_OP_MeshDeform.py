import bpy

bl_info = {
	"name": "Batch Deform Mesh",
	"description": "Facilitate the use of Mesh deform and Surface Deform",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}


class TILA_meshdeform_bind_mesh(bpy.types.Operator):
	bl_idname = "mesh.tila_meshdeform_bind_mesh"
	bl_label = "TILA : Batch meshdeform mesh"
	bl_options = {'REGISTER', 'UNDO'}

	precision : bpy.props.IntProperty(name='Precision', default=5)
	mode : bpy.props.EnumProperty(items=[("BIND", "Bind", ""), ("UNBIND", "Unbind", ""), ("UPDATE", "Update", ""), ("APPLY", "Apply", ""), ("REMOVE", "Remove", "")])
	vertex_group : bpy.props.StringProperty(name='Vertex Group', default='')


	modifier = None
	active_object = None
	compatible_type = ['MESH']
	modifier_type = 'MESH_DEFORM'
	modifier_name = 'Mesh Deform'
	processing = None
	cancelling = False

	bind_operators = bpy.ops.object.meshdeform_bind

	def init_default(self):
		self.cancelling = False
		self.processing = None

	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		if event.type == 'TIMER':
			if self.cancelling:
				self.report({'INFO'}, 'TILA batch deform : Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.process(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, 'TILA batch deform : Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def process(self, context, ob):
		if self.processing == self.active_object:
			return

		self.modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(self.modifier):
			self.modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			self.modifier = self.modifier[0]
		
		if self.mode == 'BIND':
			self.bind()
		elif self.mode == 'UNBIND':
			self.unbind()
		elif self.mode == 'UPDATE':
			self.update()
		elif self.mode == 'APPLY':
			 self.apply()
		elif self.mode == 'REMOVE':
			self.remove()

	def bind(self):
		
		bpy.context.view_layer.objects.active = self.processing
		self.modifier.object = self.active_object
		self.modifier.vertex_group = self.vertex_group
		self.modifier.precision = self.precision
		if not self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def unbind(self):
		if self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def update(self):
		self.modifier.object = self.active_object
		self.modifier.vertex_group = self.vertex_group
		self.modifier.precision = self.precision
		if self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def apply(self):
		bpy.ops.object.modifier_apply(modifier=self.modifier.name)


	def remove(self):
		bpy.ops.object.modifier_remove(modifier=self.modifier.name)


	def invoke(self, context, event):

		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]
		self.active_object = bpy.context.active_object

		if self.active_object.type not in self.compatible_type or len(self.object_to_process) <= 1:
			self.report({'ERROR'}, 'Tila Multires subdiv : no compatible object selected, select at least two meshes')
			return {'CANCELLED'} 

		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

class TILA_surfacedeform_bind_mesh(bpy.types.Operator):
	bl_idname = "mesh.tila_surfacedeform_bind_mesh"
	bl_label = "TILA : Batch surfacedeform mesh"
	bl_options = {'REGISTER', 'UNDO'}

	falloff : bpy.props.IntProperty(name='Falloff', default=4)
	strength : bpy.props.IntProperty(name='Strength', default=1)
	mode : bpy.props.EnumProperty(items=[("BIND", "Bind", ""), ("UNBIND", "Unbind", ""), ("UPDATE", "Update", ""), ("APPLY", "Apply", ""), ("REMOVE", "Remove", "")])
	vertex_group : bpy.props.StringProperty(name='Vertex Group', default='')


	modifier = None
	active_object = None
	compatible_type = ['MESH']
	modifier_type = 'SURFACE_DEFORM'
	modifier_name = 'Surface Deform'
	processing = None
	cancelling = False

	bind_operators = bpy.ops.object.surfacedeform_bind

	def init_default(self):
		self.cancelling = False
		self.processing = None

	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		if event.type == 'TIMER':
			if self.cancelling:
				self.report({'INFO'}, 'TILA batch deform : Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.process(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, 'TILA batch deform : Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def process(self, context, ob):
		if self.processing == self.active_object:
			return
			
		self.modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(self.modifier):
			self.modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			self.modifier = self.modifier[0]
		
		if self.mode == 'BIND':
			self.bind()
		elif self.mode == 'UNBIND':
			self.unbind()
		elif self.mode == 'UPDATE':
			self.update()
		elif self.mode == 'APPLY':
			 self.apply()
		elif self.mode == 'REMOVE':
			self.remove()

	def bind(self):
	
		bpy.context.view_layer.objects.active = self.processing
		self.modifier.target = self.active_object
		self.modifier.vertex_group = self.vertex_group
		self.modifier.strength = self.strength
		self.modifier.falloff = self.falloff
		if not self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def unbind(self):
		if self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def update(self):
		self.modifier.target = self.active_object
		self.modifier.vertex_group = self.vertex_group
		self.modifier.strength = self.strength
		self.modifier.falloff = self.falloff
		if self.modifier.is_bound:
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)
			self.bind_operators('INVOKE_DEFAULT', modifier=self.modifier.name)

	def apply(self):
		bpy.ops.object.modifier_apply(modifier=self.modifier.name)


	def remove(self):
		bpy.ops.object.modifier_remove(modifier=self.modifier.name)


	def invoke(self, context, event):

		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]
		self.active_object = bpy.context.active_object

		if self.active_object.type not in self.compatible_type or len(self.object_to_process) <= 1:
			self.report({'ERROR'}, 'Tila Multires subdiv : no compatible object selected, select at least two meshes')
			return {'CANCELLED'} 

		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}


classes = (
	TILA_meshdeform_bind_mesh,
	TILA_surfacedeform_bind_mesh
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()