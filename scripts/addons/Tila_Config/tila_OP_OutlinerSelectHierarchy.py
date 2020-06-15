import bpy
bl_info = {
    "name": "tila_select_hierarchy",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Mesh",
}


class OutlinerSelectHierarchy(bpy.types.Operator):
    bl_idname = "outliner.tila_select_hierarchy"
    bl_label = "TILA: select hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.outliner.collection_objects_select()
        bpy.ops.outliner.object_operation(type='SELECT_HIERARCHY')
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
