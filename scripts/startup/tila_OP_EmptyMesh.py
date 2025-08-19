import bpy
from mathutils import *

bl_info = {
	"name": "Tila : Empty Mesh",
	"author": "Tilapiatsu",
	"version": (1, 0, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D",
	"category": "Mesh",
}

class TILA_EmptyMeshOperator(bpy.types.Operator):
    bl_idname = "object.tila_emptymesh"
    bl_label = "TILA: Empty Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    emptymesh_name = 'tila_emptymesh'

    def execute(self, context):
        current_active_object = bpy.context.active_object
        if current_active_object:
            currentMode = current_active_object.mode
        else:
            currentMode = "OBJECT"

        if currentMode == "EDIT":
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = bpy.data.meshes.new(name=self.emptymesh_name)
        obj = bpy.data.objects.new(name=self.emptymesh_name, object_data=mesh)
        bpy.context.collection.objects.link(obj)

        if context.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = obj
            bpy.data.objects[obj.name].select_set(True)

        if currentMode == "EDIT":
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


addon_keymaps = []

classes = (TILA_EmptyMeshOperator,)

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
