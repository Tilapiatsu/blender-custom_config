import bpy
bl_info = {
	"name": "Export as Linked Library",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "IO",
}


class TILA_ExportAsLinkedLibrary(bpy.types.Operator):
	bl_idname = "object.tila_export_as_linked_library"
	bl_label = "TILA: outliner Export as Linked Library"
	bl_options = {'REGISTER'}


	def execute(self, context):

		return {'FINISHED'}


classes = (TILA_ExportAsLinkedLibrary,)

register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
