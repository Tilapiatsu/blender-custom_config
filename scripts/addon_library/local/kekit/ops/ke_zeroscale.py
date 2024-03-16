import bmesh
import bpy
from bpy.props import EnumProperty, IntProperty
from bpy.types import Operator
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from .._utils import average_vector


class KeZeroScale(Operator):
    bl_idname = "mesh.ke_zeroscale"
    bl_label = "ZeroScale"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    orient_type: EnumProperty(
        items=[("GLOBAL", "Global", "", "ORIENTATION_GLOBAL", 1),
               ("NORMAL", "Normal", "", "ORIENTATION_NORMAL", 2),
               ("CURSOR", "Cursor", "", "CURSOR", 3),
               ("AUTO", "Auto", "", "AUTO", 4),
               ],
        name="Orientation", options={"HIDDEN"},
        default="GLOBAL")

    screen_axis: IntProperty(default=1, min=0, max=2, options={"HIDDEN"})
    mouse_pos = Vector([0, 0])

    @classmethod
    def description(cls, context, properties):
        if properties.orient_type == "NORMAL":
            return "Zero-scale selected elements The normal of the active element.\n" \
                   "No active element = Averaged selection pos"
        elif properties.orient_type == "CURSOR":
            return "Zero-scale selected elements to the Cursor (Along the cursors Z-axis)"
        elif properties.orient_type == "AUTO":
            return "Zero-scale selected elements to nearest Vertical or Horizontal of global axis,\n" \
                   "based on mouse pos relative to active element (V or H)."
        else:
            # if properties.orient_type == "GLOBAL":
            return "Zero-scale selected elements to Vertical or Horisontal (nearest global axis to screen)"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        self.mouse_pos[0] = int(event.mouse_region_x)
        self.mouse_pos[1] = int(event.mouse_region_y)
        return self.execute(context)

    def execute(self, context):
        og_orientation = str(context.scene.transform_orientation_slots[0].type)
        og_pivot = str(context.scene.tool_settings.transform_pivot_point)
        omt = self.orient_type

        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        obj.update_from_editmode()
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        zerovalue = (1, 1, 0)
        vplane = (False, False, True)

        if self.orient_type == "CURSOR":
            avg_pos = context.scene.cursor.location
            om = context.scene.cursor.matrix.to_3x3()
        else:
            ae = bm.select_history.active
            if ae:
                aet = str(type(ae))
                if 'BMVert' in aet:
                    active_pos = ae.co
                elif 'BMEdge' in aet:
                    # use the 'end-vert' as active
                    sel_edges = [e for e in bm.edges if e.select]
                    v1 = len([e for e in ae.verts[0].link_edges if e in sel_edges])
                    v2 = len([e for e in ae.verts[1].link_edges if e in sel_edges])
                    if v1 < v2:
                        active_pos = ae.verts[0].co
                    else:
                        active_pos = ae.verts[1].co
                else:
                    vpos = [v.co for v in ae.verts]
                    active_pos = average_vector(vpos)
            else:
                vpos = [v.co for v in bm.verts if v.select]
                active_pos = average_vector(vpos)

            avg_pos = obj.matrix_world @ Vector(active_pos)
            om = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

        if self.orient_type == "AUTO" or self.orient_type == "GLOBAL":
            # Global: for use with ZeroScale H & V (using screen_axis var)
            bpy.ops.transform.select_orientation(orientation='GLOBAL')
            context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'

            rm = context.space_data.region_3d.view_matrix
            v = Vector(rm[self.screen_axis])

            if self.orient_type == "AUTO":
                # Set OMT to GLOBAL for OP use
                omt = "GLOBAL"
                # Auto: Check mouse pointer relative to active/avg_pos for H or V
                region = []
                region_data = []
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for r in area.regions:
                            if r.type == "WINDOW":
                                region = r
                                region_data = r.data

                # ap_w = obj.matrix_world @ avg_pos
                ap_2d = location_3d_to_region_2d(region, region_data, avg_pos)

                r = ap_2d - self.mouse_pos
                if abs(r[1]) < abs(r[0]):
                    v = Vector(rm[0])
                else:
                    v = Vector(rm[1])

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
            bpy.ops.transform.resize(value=zerovalue, orient_type=omt,
                                     orient_matrix_type=omt, constraint_axis=vplane, mirror=True,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False, use_proportional_projected=False,
                                     release_confirm=True)
        else:
            bpy.ops.transform.resize(value=zerovalue, orient_type=omt,
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
    
