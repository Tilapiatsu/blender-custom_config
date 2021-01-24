import bpy
from mathutils import *


class TILA_ObjectDuplicateOperator(bpy.types.Operator):
    bl_idname = "object.tila_duplicate"
    bl_label = "TILA: Duplicate Object"
    bl_options = {'REGISTER', 'UNDO'}

    linked : bpy.props.BoolProperty(name='linked', default=False)
    move : bpy.props.BoolProperty(name='move', default=False)

    def execute(self, context):
        if context.space_data.type == 'OUTLINER':
            mode = None
            if context.mode not in ['OBJECT']:
                mode = context.mode
                print(mode)
                bpy.ops.object.mode_set(mode='OBJECT')
            if self.move:
                bpy.ops.object.duplicate_move(linked=self.linked)
            else:
                bpy.ops.object.duplicate(linked=self.linked)

            if self.linked:
                bpy.ops.outliner.collection_instance()
            
            if mode is not None:
                bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

classes = (TILA_ObjectDuplicateOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
