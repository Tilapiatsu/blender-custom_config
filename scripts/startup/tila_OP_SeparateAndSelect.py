import bpy

bl_info = {
	"name": "Tila : Separate and Select",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

class TILA_SeparateAndSelect(bpy.types.Operator):
    bl_idname = "mesh.separate_and_select"        # unique identifier for buttons and menu items to reference.
    bl_label = "Separate and Select"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):

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
        bpy.ops.mesh.select_all(action='SELECT')
        return {'FINISHED'}

classes = (TILA_SeparateAndSelect,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()