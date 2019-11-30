import bpy
from bpy.props import BoolProperty


class UnwrapSelected(bpy.types.Operator):
    bl_idname = "uv.toolkit_unwrap_selected"
    bl_label = "Unwrap Selected (UVToolkit)"
    bl_description = "Unwrap selected"
    bl_options = {'REGISTER', 'UNDO'}

    update_seams: BoolProperty(name="Update seams", default=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        tool_settings = context.scene.tool_settings
        if tool_settings.use_uv_select_sync:
            self.report({'INFO'}, 'Need to disable UV Sync')
            return {'CANCELLED'}

        if self.update_seams:
            bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
        bpy.ops.uv.pin(clear=True)
        bpy.ops.uv.select_all(action='INVERT')
        bpy.ops.uv.pin(clear=False)
        bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, margin=0)
        bpy.ops.uv.pin(clear=True)
        bpy.ops.uv.select_all(action='INVERT')
        return {'FINISHED'}
