from bpy.types import Operator


class KeObjectToCursor(Operator):
    bl_idname = "view3d.ke_object_to_cursor"
    bl_label = "Align Object To Cursor"
    bl_description = "Aligns selected object(s) to Cursor (Rotation & Location)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode != "EDIT_MESH"

    def execute(self, context):
        cursor = context.scene.cursor
        c_loc = cursor.location
        c_rot = cursor.rotation_euler
        for obj in context.selected_objects:
            obj.location = c_loc
            og_rot_mode = str(obj.rotation_mode)
            obj.rotation_mode = "XYZ"
            obj.rotation_euler = c_rot
            obj.rotation_mode = og_rot_mode
            crot = obj.rotation_euler
            crot.x = round(crot.x, 4)
            crot.y = round(crot.y, 4)
            crot.z = round(crot.z, 4)
        return {'FINISHED'}
