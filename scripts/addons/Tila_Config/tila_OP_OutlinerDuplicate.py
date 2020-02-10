import bpy
from mathutils import *


class OutlinerDuplicateOperator(bpy.types.Operator):
    bl_idname = "outliner.tila_duplicate"
    bl_label = "TILA: Empty Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    linked : bpy.props.BoolProperty(name='linked', default=False)

    def execute(self, context):
        if context.space_data.type == 'OUTLINER':
            bpy.ops.object.duplicate(linked=self.linked)

        return {'FINISHED'}



def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
