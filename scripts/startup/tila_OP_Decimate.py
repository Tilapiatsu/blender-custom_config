import bpy

bl_info = {
	"name": "Tila : Decimate",
	"description": "Facilitate the use of the decimation modifier",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}


class TILA_decimate(bpy.types.Operator):
	bl_idname = "object.tila_decimate"
	bl_label = "TILA : Decimate"
	bl_options = {'REGISTER', 'UNDO'}


	ratio : bpy.props.FloatProperty(name='Ratio', default=1)
	use_symmetry : bpy.props.BoolProperty(name='Symmetry', default=False)
	symmetry_axis : bpy.props.EnumProperty(name='Symmetry Axis', items=[("X", "x", ""), ("Y", "y", ""), ("Z", "z", "")])
	use_collapse_triangulate : bpy.props.BoolProperty(name='Triangulate', default=False)
	# convert_to_mesh : bpy.props.BoolProperty(name='Convert To Mesh', default=False)


	decimate_modifier = None
	active_object = None
	modifier_name = 'Decimate'
	modifier_type = 'DECIMATE'
	compatible_type = ['MESH']
	processing = None

	cancelling = False

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text='Decimate Settings')
		col.prop(self, 'ratio')
		row = col.row()
		row.prop(self, 'use_symmetry')
		row = col.row()
		row.props_enum(self, 'symmetry_axis')
		if not self.use_symmetry:
			row.active = False
		col.prop(self, 'use_collapse_triangulate')
		# col.prop(self, 'convert_to_mesh')

	def init_default(self):
		self.cancelling = False
		self.processing = None
		self.decimate_modifier = None

	def execute(self, context):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]
		for o in self.object_to_process:
			self.decimate(context, o)

		self.init_default()
		return {'FINISHED'}

		# self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		# bpy.context.window_manager.modal_handler_add(self)

		# return {"RUNNING_MODAL"}

	def decimate(self, context, ob):
		self.decimate_modifier = [m for m in ob.modifiers if m.type == self.modifier_type]

		if not len(self.decimate_modifier):
			self.decimate_modifier = ob.modifiers.new(name=self.modifier_name, type=self.modifier_type)
		else:
			self.decimate_modifier = self.decimate_modifier[0]


		self.decimate_modifier.ratio = self.ratio
		self.decimate_modifier.use_symmetry = self.use_symmetry
		self.decimate_modifier.symmetry_axis = self.symmetry_axis
		self.decimate_modifier.use_collapse_triangulate = self.use_collapse_triangulate

	def modal(self, context, event):
		if event.type == 'ESC':
			self.cancelling = True

		if event.type == 'TIMER':
			if self.cancelling:
				self.report({'INFO'}, 'TILA Decimate : Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				self.decimate(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, 'TILA Decimate : Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def invoke(self, context, event):
		wm = bpy.context.window_manager
		return wm.invoke_props_popup(self, event)


classes = (
	TILA_decimate,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()