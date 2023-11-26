from math import radians

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator


class KeAlignOriginToSelected(Operator):
    bl_idname = "view3d.align_origin_to_selected"
    bl_label = "Align Origin To Selected Elements"
    bl_description = "Edit Mode: Places origin(s) at element selection (+orientation)\n" \
                     "Object Mode (1 selected): Set Origin to geo Center\n" \
                     "Object Mode (2 selected): Set Origin to 2nd Obj Origin\n"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER', 'UNDO'}

    invert_z : BoolProperty(default=True, name="Invert Z-Axis", description="Invert Z-Axis in Edit Mode")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        cursor = context.scene.cursor
        ogmode = str(cursor.rotation_mode)
        ogloc = cursor.location.copy()
        ogrot = cursor.rotation_quaternion.copy()

        if context.mode == "EDIT_MESH":
            cursor.rotation_mode = "QUATERNION"
            bpy.ops.view3d.cursor_fit_selected_and_orient()
            if self.invert_z:
                cursor.rotation_mode = "XYZ"
                cursor.rotation_euler.rotate_axis('Y', radians(180.0))
            bpy.ops.view3d.ke_origin_to_cursor(align="BOTH")
            bpy.ops.transform.select_orientation(orientation='LOCAL')
            context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        else:
            target_obj = None
            sel_obj = [o for o in context.selected_objects]
            if sel_obj:
                sel_obj = [o for o in sel_obj]
            if context.active_object:
                target_obj = context.active_object
            if target_obj is None and sel_obj:
                target_obj = sel_obj[-1]
            if not target_obj:
                return {'CANCELLED'}

            sel_obj = [o for o in sel_obj if o != target_obj]

            # Center to mesh if only one object selected and active
            if not sel_obj and target_obj:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            else:
                cursor.rotation_mode = "XYZ"
                cursor.location = target_obj.matrix_world.translation
                cursor.rotation_euler = target_obj.rotation_euler
                bpy.ops.object.select_all(action='DESELECT')

                for o in sel_obj:
                    o.select_set(True)
                    bpy.ops.view3d.ke_origin_to_cursor(align="BOTH")
                    o.select_set(False)

                for o in sel_obj:
                    o.select_set(True)

        cursor.location = ogloc
        cursor.rotation_mode = "QUATERNION"
        cursor.rotation_quaternion = ogrot
        cursor.rotation_mode = ogmode

        return {"FINISHED"}
