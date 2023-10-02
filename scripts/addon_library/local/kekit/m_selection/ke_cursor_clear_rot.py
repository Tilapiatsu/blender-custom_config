from bpy.types import Operator


class KeCursorClearRot(Operator):
    bl_idname = "view3d.ke_cursor_clear_rot"
    bl_label = "Clear Cursor Rotation"
    bl_description = "Clear the cursor's rotation (only)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        c = context.scene.cursor
        if c.rotation_mode == "QUATERNION":
            c.rotation_quaternion = 1, 0, 0, 0
        elif c.rotation_mode == "AXIS_ANGLE":
            c.rotation_axis_angle = 0, 0, 1, 0
        else:
            c.rotation_euler = 0, 0, 0

        return {'FINISHED'}
