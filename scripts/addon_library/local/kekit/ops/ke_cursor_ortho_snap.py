from math import copysign

from bpy.types import Operator
from mathutils import Vector, Quaternion


class KeCursorOrthoSnap(Operator):
    bl_idname = "view3d.ke_cursor_ortho_snap"
    bl_label = "Cursor Otho Snap"
    bl_description = "Snap-Aligns the Cursor Z-axis to the nearest world (ortho) axis, relative to the viewport camera"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        # 90 Degree Value (for quat)
        ndv = 0.7071068286895752
        cursor = context.scene.cursor
        og_mode = str(cursor.rotation_mode)
        rm = context.space_data.region_3d.view_matrix
        v = Vector(rm[2])
        x, y, z = abs(v.x), abs(v.y), abs(v.z)

        if x > y and x > z:
            axis = copysign(1, v.x), 0, 0
        elif y > x and y > z:
            axis = 0, copysign(1, v.y), 0
        else:
            axis = 0, 0, copysign(1, v.z)

        if sum(axis) < 0:
            if bool(axis[2]):
                q = Quaternion((-0.0, ndv, ndv, 0.0))
            elif bool(axis[1]):
                q = Quaternion((ndv, ndv, 0.0, 0.0))
            else:
                q = Quaternion((ndv, 0.0, -ndv, 0.0))
        else:
            if bool(axis[2]):
                q = Quaternion((ndv, 0.0, 0.0, -ndv))
            elif bool(axis[1]):
                q = Quaternion((ndv, -ndv, 0.0, 0.0))
            else:
                q = Quaternion((ndv, 0.0, ndv, 0.0))

        cursor.rotation_mode = "QUATERNION"
        cursor.rotation_quaternion = q
        cursor.rotation_mode = og_mode

        return {'FINISHED'}
