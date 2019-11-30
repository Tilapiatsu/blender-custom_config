import bpy
from bpy.props import FloatVectorProperty


class AlignToCursor(bpy.types.Operator):
    bl_idname = "uv.toolkit_align_to_cursor"
    bl_label = "Align to Cursor (UVToolkit)"
    bl_description = "Align to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    align_to_cursor: FloatVectorProperty(name="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        curent_pivot = context.space_data.pivot_point
        context.space_data.pivot_point = 'CURSOR'
        bpy.ops.transform.resize('EXEC_DEFAULT', value=self.align_to_cursor)
        context.space_data.pivot_point = curent_pivot
        return {'FINISHED'}
