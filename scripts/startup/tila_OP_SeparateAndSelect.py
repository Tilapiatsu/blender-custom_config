import bpy
import bmesh

bl_info = {
	"name": "Tila : Separate and Select",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

def get_selected_objects():
	selected_objects = bpy.context.objects_in_mode
	objs = [o for o in selected_objects if o.data.total_vert_sel]
	return objs

class TILA_SeparateAndSelect(bpy.types.Operator):
	bl_idname = "mesh.separate_and_select"        # unique identifier for buttons and menu items to reference.
	bl_label = "Separate and Select"         # display name in the interface.
	bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

	by_loose_parts : bpy.props.BoolProperty(name='By Loose Part', default=False) 

	@classmethod
	def poll(cls, context):
		if not len(context.selected_objects):
			return False
		
		selected = False

		objs = get_selected_objects()

		if len(objs):
			selected = True
		
		if not selected:
			print('Please select at least an element')

		return selected
	
	def separate_selected(self, context):
		bpy.ops.mesh.separate(type='SELECTED')

		extracted_objects = []
		for p in context.selected_objects:
			if p.mode != 'EDIT':
				extracted_objects.append(p)

		bpy.ops.object.editmode_toggle()

		bpy.ops.object.select_all(action='DESELECT')
		i=0
		for o in extracted_objects:
			o.select_set(True)
			if i == 0:
				context.view_layer.objects.active = o
				i += 1
				
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.select_all('INVOKE_DEFAULT', action='SELECT')

		self.separated = True

	def select_next_polygon_island(self):
		me = self.current_object_to_proceed.data
		bm = bmesh.from_edit_mesh(me)
		faces = bm.faces
		
		if not len(faces):
			return True

		faces[0].select = True  # select index 0
		
		# Show the updates in the viewport
		bmesh.update_edit_mesh(me)

		bpy.ops.mesh.select_linked()

		return False

	def modal(self, context, event):
		if self.finished or self.cancelled:
			return {'FINISHED'}
		
		if event.type in ['ESC']:
			self.cancelled = True

		if event.type in ['TIMER']:
			if self.current_object_to_proceed is None:
				self.current_object_to_proceed = self.objects_to_proceed.pop()

			if not self.separated:
				bpy.ops.mesh.select_all(action='INVERT')

				if not self.current_object_to_proceed.data.total_face_sel:
					self.finished = True
					return {'PASS_THROUGH'}
				
				self.separate_selected(context)
				self.current_object_to_proceed = bpy.context.view_layer.objects.active 
			else:
				bpy.ops.mesh.select_all(action='DESELECT')
				self.select_next_polygon_island()
				self.separated = False

		return {'PASS_THROUGH'}

	def execute(self, context):
		self.objects_to_proceed = get_selected_objects()
		self.current_object_to_proceed = self.objects_to_proceed.pop()
		if self.by_loose_parts:
			self.separated = False
			self.cancelled = False
			self.finished = False
			wm = context.window_manager
			self._timer = wm.event_timer_add(0.1, window=context.window)
			wm.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.separate_selected(context)
			return {'FINISHED'}

classes = (TILA_SeparateAndSelect,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
	register()