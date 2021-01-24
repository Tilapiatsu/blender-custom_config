import bpy
bl_info = {
	"name": "grou_selected",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}


class TILA_GroupSelected(bpy.types.Operator):
	bl_idname = "outliner.tila_group_selected"
	bl_label = "TILA: Group Selected"
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.EnumProperty(items=[("GROUP_TO_BIGGER_NUMBER", "Group To Bigger Number", ""), ("GROUP_TO_ACTIVE", "Group To Active", ""), ("MOVE_TO_ACTIVE", "Move To Active", ""), ("ADD_TO_ACTIVE", "Add To Active", "")])

	def get_parent_collection(self, context):
		parent_collection = ''
		if self.mode == 'GROUP_TO_BIGGER_NUMBER':
			collections = {}

			for o in context.selected_objects:
				collection_name = o.users_collection[0].name
				if collection_name not in collections.keys():
					collections[o.users_collection[0].name] = 1
				else:
					collections[o.users_collection[0].name] += 1
			
			parent_collection = ''
			max_item = 0
			for c,n in collections.items():
				if n>max_item:
					max_item = n
					parent_collection = c
		
		elif self.mode in ('GROUP_TO_ACTIVE', 'MOVE_TO_ACTIVE') :
			parent_collection = context.view_layer.objects.active.users_collection[0].name


		return parent_collection

	def execute(self, context):
		parent_collection_name = self.get_parent_collection(context)
		parent_collection = bpy.data.collections[parent_collection_name]

		if self.mode in ['MOVE_TO_ACTIVE', 'ADD_TO_ACTIVE']:
			new_collection = parent_collection
		else:
			new_collection_name = parent_collection_name + '_group'
			new_collection = bpy.data.collections.new(new_collection_name)
			parent_collection.children.link(new_collection)


		for o in context.selected_objects:
			if self.mode not in ['ADD_TO_ACTIVE']:
				o.users_collection[0].objects.unlink(o)
			new_collection.objects.link(o)
			


		return {'FINISHED'}

classes = (TILA_GroupSelected,)

register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
