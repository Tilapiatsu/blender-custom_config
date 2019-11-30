import bpy
from bpy.props import FloatProperty


class RotateUVIslands(bpy.types.Operator):
    bl_idname = "uv.toolkit_rotate_uv_islands"
    bl_label = "Rotate selected UV islands (UVToolkit)"
    bl_description = "Rotate selected UV islands"
    bl_options = {'REGISTER', 'UNDO'}

    angle: FloatProperty(name="angle", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        curent_pivot = context.space_data.pivot_point
        context.space_data.pivot_point = 'CENTER'
        bpy.ops.transform.rotate(value=self.angle)
        context.space_data.pivot_point = curent_pivot
        return {'FINISHED'}
