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
        currentActiveObject = bpy.context.active_object
        if currentActiveObject:
            currentMode = currentActiveObject.mode
        else:
            currentMode = "OBJECT"

        currentSelection = bpy.context.selected_objects

        if currentMode == "EDIT":
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.mesh.primitive_plane_add(align='WORLD', enter_editmode=False, location=(0.0, 0.0, 0.0))
        bpy.context.object.data.name = self.emptymesh_name
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.selected_objects[0].name = "EmptyMesh"

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
