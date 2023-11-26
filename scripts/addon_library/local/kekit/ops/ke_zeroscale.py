import bmesh
import bpy
from bpy.props import EnumProperty, IntProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import average_vector


class KeZeroScale(Operator):
    bl_idname = "mesh.ke_zeroscale"
    bl_label = "ZeroScale"
    bl_description = "Instantly zero-scales selected elements to A: Vertical or Horisontal screen global axis (pie)" \
                     "B: The normal of the active element. No active element = Average selection pos. (pie)" \
                     "C: To the Cursor (mind the rotation!)"
    bl_options = {'REGISTER', 'UNDO'}

    orient_type: EnumProperty(
        items=[("GLOBAL", "Global", "", "GLOBAL", 1),
               ("NORMAL", "Normal", "", "NORMAL", 2),
               ("CURSOR", "Cursor", "", "CURSOR", 3),
               ],
        name="Orientation", options={"HIDDEN"},
        default="GLOBAL")

    screen_axis: IntProperty(default=1, min=0, max=2, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        og_orientation = str(context.scene.transform_orientation_slots[0].type)
        og_pivot = str(context.scene.tool_settings.transform_pivot_point)

        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        obj.update_from_editmode()
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        omt = self.orient_type
        zerovalue = (1, 1, 0)
        vplane = (False, False, True)

        if self.orient_type == "CURSOR":
            avg_pos = context.scene.cursor.location
            om = context.scene.cursor.matrix.to_3x3()
        else:
            if bm.select_history.active:
                if sel_mode[0]:
                    active_pos = bm.select_history[-1].co
                else:
                    vpos = [v.co for v in bm.select_history[-1].verts]
                    active_pos = average_vector(vpos)
            else:
                vpos = [v.co for v in bm.verts if v.select]
                active_pos = average_vector(vpos)

            avg_pos = obj.matrix_world @ Vector(active_pos)
            om = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

        if self.orient_type == "GLOBAL":
            # Note: "Global" is only for use with ZeroScale H & V (using screen_axis var)
            bpy.ops.transform.select_orientation(orientation='GLOBAL')
            context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'

            rm = context.space_data.region_3d.view_matrix
            v = Vector(rm[self.screen_axis])
            xz = abs(Vector((0, 1, 0)).dot(v))
            xy = abs(Vector((0, 0, 1)).dot(v))
            yz = abs(Vector((1, 0, 0)).dot(v))

            value_dic = {(True, False, True): xz, (True, True, False): xy, (False, True, True): yz}
            lock_dic = {(False, True, False): xz, (False, False, True): xy, (True, False, False): yz}

            vplane = sorted(value_dic, key=value_dic.get)[-1]
            zerovalue = [float(i) for i in vplane]
            vplane = sorted(lock_dic, key=lock_dic.get)[-1]

        elif self.orient_type == "NORMAL":
            vplane = (False, False, True)
            context.scene.transform_orientation_slots[0].type = 'NORMAL'
            context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
            if sel_mode[1]:
                zerovalue = (0, 1, 0)
            else:
                zerovalue = (1, 1, 0)

        if self.orient_type == "NORMAL":
            bpy.ops.transform.resize(value=zerovalue, orient_type=self.orient_type,
                                     orient_matrix_type=omt, constraint_axis=vplane, mirror=True,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False, use_proportional_projected=False,
                                     release_confirm=True)
        else:
            bpy.ops.transform.resize(value=zerovalue, orient_type=self.orient_type,
                                     orient_matrix=om,
                                     orient_matrix_type=omt, constraint_axis=vplane, mirror=False,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                     proportional_size=1.0,
                                     use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                     snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0),
                                     gpencil_strokes=False, texture_space=False,
                                     remove_on_cancel=False, center_override=avg_pos, release_confirm=False)

        bpy.ops.transform.select_orientation(orientation=og_orientation)
        context.scene.tool_settings.transform_pivot_point = og_pivot

        self.orient_type = "GLOBAL"

        return {'FINISHED'}
    
