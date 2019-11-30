import bpy
from bpy.props import FloatVectorProperty


class MoveUvIslands(bpy.types.Operator):
    bl_idname = "uv.toolkit_move_islands"
    bl_label = "Move islands (UVToolkit)"
    bl_description = "Move islands"
    bl_options = {'REGISTER', 'UNDO'}

    move_uv: FloatVectorProperty(name="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.transform.translate('EXEC_DEFAULT', value=self.move_uv)
        return {'FINISHED'}
