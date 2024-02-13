from math import radians

import bpy
from bpy.types import Operator
from bpy.props import IntProperty
from mathutils import Matrix, Vector


class KeStepRotate(Operator):
    bl_idname = "view3d.ke_vp_step_rotate"
    bl_label = "VP Step Rotate"
    bl_description = "Rotate object or selected elements given angle, based on viewport relative to the object.\n" \
                     "Local, Cursor & View - else Global orientation."
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    rot: IntProperty(min=-180, max=180, default=90)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.space_data.type == "VIEW_3D"

    def execute(self, context):
        obj = context.object
        val = self.rot
        tos = bpy.context.scene.transform_orientation_slots[0].type

        rm = context.space_data.region_3d.view_matrix
        ot = "GLOBAL"
        tm = Matrix().to_3x3()

        if tos == "LOCAL":
            ot = "LOCAL"
            tm = obj.matrix_world.to_3x3().normalized()
        elif tos == "VIEW":
            ot = "VIEW"
            tm = context.space_data.region_3d.view_matrix.inverted().to_3x3()
        elif tos == "CURSOR":
            ot = "CURSOR"
            tm = context.scene.cursor.matrix.to_3x3()
        # else defaults to Global for now

        v = tm.inverted() @ Vector(rm[2]).to_3d()
        x, y, z = abs(v[0]), abs(v[1]), abs(v[2])
        nx, ny, nz = v[0], v[1], v[2]

        if x > y and x > z:
            axis = True, False, False
            oa = "X"
            flip = nx
        elif y > x and y > z:
            axis = False, True, False
            oa = "Y"
            flip = ny
        else:
            axis = False, False, True
            oa = "Z"
            flip = nz

        # check for axis inverse (to work with directions in pie menu (view) )
        if flip > 0:
            val *= -1

        bpy.ops.transform.rotate(value=radians(val), orient_axis=oa, orient_type=ot, orient_matrix_type=ot,
                                 constraint_axis=axis, mirror=True, use_proportional_edit=False,
                                 proportional_edit_falloff='SMOOTH', proportional_size=1,
                                 use_proportional_connected=False, use_proportional_projected=False)

        # QnD Quat-conversion to keet rotation values sane (and fp-rounded)
        r = obj.rotation_euler.to_quaternion().to_euler()
        obj.rotation_euler.x = round(r.x, 4)
        obj.rotation_euler.y = round(r.y, 4)
        obj.rotation_euler.z = round(r.z, 4)

        return {"FINISHED"}
