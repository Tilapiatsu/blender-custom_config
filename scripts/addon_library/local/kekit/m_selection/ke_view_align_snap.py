from math import copysign
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import get_selected


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

            # Negative: FRONT (-Y), LEFT(-X), BOTTOM (-Z)
            if sum(axis) < 0:
                if bool(axis[2]):
                    bpy.ops.view3d.view_axis(type='BOTTOM')
                elif bool(axis[1]):
                    bpy.ops.view3d.view_axis(type='FRONT')
                else:
                    bpy.ops.view3d.view_axis(type='LEFT')
            else:
                if bool(axis[2]):
                    bpy.ops.view3d.view_axis(type='TOP')
                elif bool(axis[1]):
                    bpy.ops.view3d.view_axis(type='BACK')
                else:
                    bpy.ops.view3d.view_axis(type='RIGHT')

        return {'FINISHED'}
