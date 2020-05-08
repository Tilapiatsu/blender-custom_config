import bpy

bl_info = {
	"name": "Smart Join",
	"description": "Allow to apply modifiers and or duplicate meshes before Joining two objects",
	"author": ("Tilapiatsu"),
	"version": (1, 0, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"wiki_url": "",
	"category": "3D View"
}


class TILA_smart_join(bpy.types.Operator):
	bl_idname = "object.tila_smart_join"
	bl_label = "TILA : Smart Join"
	bl_options = {'REGISTER', 'UNDO'}

	apply_modifiers : bpy.props.BoolProperty(name='Apply Modifiers', default=False)
	duplicate : bpy.props.BoolProperty(name='Duplicate Objects', default=False)

	compatible_type = ['MESH', 'CURVE']


	def invoke(self, context, event):

		self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]

		if not len(self.object_to_process):
			return {'CANCELLED'}

		if self.duplicate:
			bpy.ops.object.duplicate(mode='INIT')
			self.object_to_process = [o for o in bpy.context.selected_objects if o.type in self.compatible_type]


		if self.apply_modifiers:
			for o in self.object_to_process:
				bpy.context.view_layer.objects.active = o
				bpy.ops.object.apply_all_modifiers()
		
		bpy.ops.object.join()

		return {'FINISHED'}

classes = (
	TILA_smart_join
)
# register, unregister = bpy.utils.register_classes_factory(classes)


def register():
	pass


def unregister():
	pass


if __name__ == "__main__":
	register()
