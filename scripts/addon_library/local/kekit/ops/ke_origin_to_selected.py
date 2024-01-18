import bpy
from bpy.types import Operator


def restore_cursor(cursor, loc, rot, ogmode):
    cursor.location = loc
    cursor.rotation_mode = "QUATERNION"
    cursor.rotation_quaternion = rot
    cursor.rotation_mode = ogmode


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
                context.object.type in {'MESH', "CURVE"})

    def execute(self, context):
        # Need to assign all of these vars, due to the context override
        cursor = context.scene.cursor
        rot = cursor.rotation_quaternion.copy()
        loc = cursor.location.copy()
        ogmode = str(cursor.rotation_mode)

        editmode = True if context.mode == "EDIT_MESH" else False
        curve = True if context.mode == "EDIT_CURVE" else False

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                context = context.copy()
                context['area'] = area
                context['region'] = area.regions[-1]

                if editmode:
                    bpy.ops.view3d.snap_cursor_to_center()
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                    restore_cursor(cursor, loc, rot, ogmode)
                elif curve:
                    bpy.ops.view3d.snap_cursor_to_selected()
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.view3d.ke_origin_to_cursor(align="LOCATION")
                    restore_cursor(cursor, loc, rot, ogmode)
                else:
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                break

        return {'FINISHED'}
