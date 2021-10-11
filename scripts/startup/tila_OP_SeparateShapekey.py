import bpy

bl_info = {
	"name": "Batch Separate Shapekey",
	"description": "Separate one single Skapekey or explode all shapekeys",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"doc_url": "",
	"category": "3D View"
}


class TILA_SeparateShapeKey(bpy.types.Operator):
	bl_idname = "object.tila_separate_shape_key"
	bl_label = "TILA : Batch separate ShapeKey from object"
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.EnumProperty(items=[("EXPLODE", "Explode", ""), ("NAME", "Name", "")], default="EXPLODE")
	shapekey_name : bpy.props.StringProperty(name='Shapekey Name', default='')

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
				self.report({'INFO'}, 'TILA batch deform : Cancelled')
				return {"FINISHED"}

			elif self.processing is not None:
				return {"PASS_THROUGH"}

			elif self.processing is None and len(self.object_to_process):
				self.processing = self.object_to_process.pop()
				print('Tila Separate ShapeKey : Processing object "{}"'.format(self.processing.name))
				self.process(context, self.processing)
				self.processing = None

			else:
				self.report({'INFO'}, 'TILA Separate Shapekey : Complete')
				bpy.context.window_manager.event_timer_remove(self._timer)
				self.init_default()
				return {"FINISHED"}

		return {"PASS_THROUGH"}

	def process(self, context, ob):
		shapekey_name_list = ob.data.shape_keys.key_blocks.keys()
		bpy.ops.object.select_all(action='DESELECT')

		if self.mode == "EXPLODE":
			for sk in shapekey_name_list:
				self.extract_shapekey(context, ob, shapekey_name_list, sk)
				bpy.ops.object.select_all(action='DESELECT')
				
		elif self.mode == "NAME":
			if not len(self.shapekey_name):
				print('Tila Separate ShapeKey : shapekey_name should be specified')
				return

			self.extract_shapekey(context, ob, shapekey_name_list, self.shapekey_name)
		
		bpy.ops.object.select_all(action='DESELECT')
						
	def extract_shapekey(self, context, ob, shapekey_name_list, shapekey_name):
		ob.select_set(True)
		context.view_layer.objects.active = ob
		bpy.ops.object.duplicate(mode='INIT')
		duplicate = bpy.context.view_layer.objects.active
		duplicate.name = ob.name + "_" + shapekey_name

		index_target = self.shapekey_set_active_by_name(duplicate, shapekey_name)

		if index_target is None: 
			return
			
		else: # Shapekey_name exist in the current object_to_process
			base = shapekey_name_list[0]
			others = shapekey_name_list[1:]
			for sk in others:
				if sk == shapekey_name:
					self.shapekey_set_mute_by_name(ob, sk, False)
					self.shapekey_set_value_by_name(ob, sk, 1.0)
				else:
					index = self.shapekey_set_active_by_name(duplicate, sk)
					if index is not None:
						print('Tila Separate ShapeKey : Removing shapekey "{}" on object "{}"'.format(sk, duplicate.name))
						bpy.ops.object.shape_key_remove()
			
			# remove Base
			index = self.shapekey_set_active_by_name(duplicate, base)
			if index is not None:
				bpy.ops.object.shape_key_remove()

			# # remove TargetShapeKey
			index = self.shapekey_set_active_by_name(duplicate, shapekey_name)
			if index is not None:
				bpy.ops.object.shape_key_remove()

	def shapekey_set_active_by_name(self, ob, shapekey_name:str):
		""" Set the shapekey  nameed "shapekey_name" of the object "ob" active

		retrun: the index of the active shapekey or None if not found
		"""
		def return_none():
			print('Tila Separate ShapeKey : Shapekey "{}" not found in object "{}"'.format(shapekey_name, ob.name))
			return None
		try:
			if ob.data.shape_keys is None:
				return return_none()
			index = ob.data.shape_keys.key_blocks.keys().index(shapekey_name)
		except ValueError or AttributeError:
			return return_none()

		# setting active shapekey
		ob.active_shape_key_index = index
		return index

	def shapekey_set_mute_by_name(self, ob, shapekey_name:str, mute:bool = True):
		""" Set the mute of the shapekey named "shapekey_name" of the object "ob" to "mute"

		retrun: the mute or None if the shapekey doesn't exist
		"""
		def return_none():
			print('Tila Separate ShapeKey : Shapekey "{}" not found in object "{}"'.format(shapekey_name, ob.name))
			return None
		try:
			if ob.data.shape_keys is None:
				return return_none()
			index = ob.data.shape_keys.key_blocks.keys().index(shapekey_name)
		except ValueError or AttributeError:
			return return_none()

		# setting mute value
		ob.data.shape_keys.key_blocks[index].mute = mute
		return mute

	def shapekey_set_value_by_name(self, ob, shapekey_name:str, value:float):
		""" Set the value of the shapekey named "shapekey_name" of the object "ob" to "value"

		retrun: the value or None if the shapekey doesn't exist
		"""
		def return_none():
			print('Tila Separate ShapeKey : Shapekey "{}" not found in object "{}"'.format(shapekey_name, ob.name))
			return None
		try:
			if ob.data.shape_keys is None:
				return return_none()
			index = ob.data.shape_keys.key_blocks.keys().index(shapekey_name)
		except ValueError or AttributeError:
			return return_none()

		# setting mute value
		ob.data.shape_keys.key_blocks[index].mute = value
		return value

	def invoke(self, context, event):
		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		if self.mode == "NAME":
			wm = context.window_manager
			return wm.invoke_props_dialog(self)
		else:
			return self.execute(context)
			
	def execute(self, context):
		self._timer = bpy.context.window_manager.event_timer_add(0.1, window=bpy.context.window)
		bpy.context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.label(text='Enter name of the shapekey you want to separate')
		col.prop(self, 'shapekey_name')

classes = (
	TILA_SeparateShapeKey,
)


register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()