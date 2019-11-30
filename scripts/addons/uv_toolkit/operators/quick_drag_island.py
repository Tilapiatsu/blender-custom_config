import bpy
from bpy.props import BoolProperty


class QuickDragIsland(bpy.types.Operator):
    bl_idname = "uv.toolkit_quick_drag_island"
    bl_label = "Quick Drag Island (UVToolkit)"
    bl_description = "Quick drag island"
    bl_options = {'REGISTER', 'UNDO'}

    select_island: BoolProperty(name="Select Island", default=True, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        tool_settings = context.scene.tool_settings
        if tool_settings.use_uv_select_sync:
            current_mode = tuple(context.tool_settings.mesh_select_mode)
            context.tool_settings.mesh_select_mode = (False, False, True)  # Face
            bpy.ops.uv.select_all(action='DESELECT')
            bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT')
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            if self.select_island is not True:
                bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT', deselect=True)
            context.tool_settings.mesh_select_mode = current_mode
        else:
            bpy.ops.uv.select_all(action='DESELECT')
            bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT')
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            if self.select_island is not True:
                bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT', deselect=True)
        return {'FINISHED'}
