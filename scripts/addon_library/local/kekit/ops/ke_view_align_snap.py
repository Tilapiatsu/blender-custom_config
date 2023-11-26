from math import copysign
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector, Quaternion
from .._utils import get_selected


def find_zrot(q):
    z_rotations = [
        # Top (skip default pick)
        Quaternion((0.0, 0.0, 0.0, -1.0)),
        Quaternion((-0.7071, 0.0, 0.0, -0.7071)),
        Quaternion((0.7071, 0.0, 0.0, -0.7071)),
        # Bottom
        Quaternion((0.0, 0.7071, 0.7071, 0.0)),
        Quaternion((0.0, 1.0, 0.0, 0.0)),
        Quaternion((0.0, -0.7071, 0.7071, 0.0)),
        Quaternion((0.0, 0.0, 1.0, 0.0))
    ]
    # Default pick
    pick = Quaternion((1.0, 0.0, 0.0, 0.0))
    pick_d = abs(pick.dot(q))
    # Find best pick
    for r in z_rotations:
        d = abs(r.dot(q))
        if d > pick_d:
            pick = r
            pick_d = d
    return pick


class KeViewAlignSnap(Operator):
    bl_idname = "view3d.ke_view_align_snap"
    bl_label = "View Align Snap"
    bl_description = "Snap view to nearest Orthographic. Note: No toggle - just rotate view back to perspective"
    bl_options = {'REGISTER'}

    contextual: BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        sel = []
        slot = []
        if self.contextual:
            slot = context.scene.kekit_temp.viewtoggle
            obj = get_selected(context)
            if obj:
                obj.update_from_editmode()
                sel = [v for v in obj.data.vertices if v.select]

        # ALIGN TO SELECTED (TOGGLE)
        if sel or sum(slot) != 0:
            bpy.ops.view3d.ke_view_align_toggle()
        else:
            # OR SNAP TO NEAREST ORTHO
            rm = context.space_data.region_3d.view_matrix
            v = Vector(rm[2])
            x, y, z = abs(v.x), abs(v.y), abs(v.z)

            if x > y and x > z:
                axis = copysign(1, v.x), 0, 0
            elif y > x and y > z:
                axis = 0, copysign(1, v.y), 0
            else:
                axis = 0, 0, copysign(1, v.z)

            # For better z axis snapping:
            rv3d = context.space_data.region_3d
            vrot = rv3d.view_rotation
            # Note: Still using the ops to be able to "mouse rotate off" ortho (back to persp)

            # Negative: FRONT (-Y), LEFT(-X), BOTTOM (-Z)
            if sum(axis) < 0:
                if bool(axis[2]):
                    zrot = find_zrot(vrot)
                    bpy.ops.view3d.view_axis(type='BOTTOM')
                    rv3d.view_rotation = zrot
                elif bool(axis[1]):
                    bpy.ops.view3d.view_axis(type='FRONT')
                else:
                    bpy.ops.view3d.view_axis(type='LEFT')
            else:
                if bool(axis[2]):
                    zrot = find_zrot(vrot)
                    bpy.ops.view3d.view_axis(type='TOP')
                    rv3d.view_rotation = zrot
                elif bool(axis[1]):
                    bpy.ops.view3d.view_axis(type='BACK')
                else:
                    bpy.ops.view3d.view_axis(type='RIGHT')

        return {'FINISHED'}
