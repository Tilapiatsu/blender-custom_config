import bpy
from bpy.types import Operator


class KeOriginToSelected(Operator):
    bl_idname = "view3d.origin_to_selected"
    bl_label = "Origin To Selected Elements"
    bl_description = "Places origin(s) at element selection average\n" \
                     "(Location Only, Apply rotation for world rotation)"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        # Need to assign all of these vars, due to the context override
        obj = context.object
        cursor = context.scene.cursor
        rot = cursor.rotation_quaternion.copy()
        loc = cursor.location.copy()
        ogmode = str(cursor.rotation_mode)
        obj_type = obj.type

        editmode = False if context.mode != "EDIT_MESH" else True
        if obj_type == "CURVE":
            editmode = False if context.mode != "EDIT_CURVE" else True

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                context = context.copy()
                context['area'] = area
                context['region'] = area.regions[-1]

                if not editmode :
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                else:
                    bpy.ops.view3d.snap_cursor_to_center()
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                    cursor.location = loc
                    cursor.rotation_mode = "QUATERNION"
                    cursor.rotation_quaternion = rot
                    cursor.rotation_mode = ogmode
                    break

        return {'FINISHED'}
