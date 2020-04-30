bl_info = {
    "name": "MouseMirror",
    "author": "Kjell Emanuelsson 2020",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
}
import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_location_3d
from .ke_utils import average_vector, correct_normal, flatten, get_islands, rotation_from_vector


class VIEW3D_OT_ke_mouse_mirror(Operator):
    bl_idname = "view3d.ke_mouse_mirror"
    bl_label = "Mouse Mirror"
    bl_description = "Mirror (resize) selection using relative global mouse position (over selection = Z axis etc.)"
    bl_options = {'REGISTER'}

    center: bpy.props.EnumProperty(items=[("BBOX", "Bounding Box", ""),
                                ("ACTIVE", "Active (obj:World Axis)", ""),
                                ("CURSOR", "Cursor", "")],
                                 name="Center", default="BBOX")

    use_center: bpy.props.BoolProperty(name="Active/Cursor as center", default=True)

    mouse_pos = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        if context.object.data.is_editmode:
            if not self.center == "ACTIVE":
                bpy.ops.mesh.duplicate()
        else:
            # GRAB CURRENT ORIENT & PIVOT (to restore at the end)
            og_orientation = bpy.context.scene.transform_orientation_slots[0].type
            og_pivot = bpy.context.scene.tool_settings.transform_pivot_point
            # SET TO GLOBAL
            bpy.ops.transform.select_orientation(orientation='GLOBAL')
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            # DUPE
            bpy.ops.object.duplicate()
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
        obj = bpy.context.object
        obj_mtx = obj.matrix_world.copy()
        om = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        scale_value = None

        if context.object.data.is_editmode:
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            vpos = None

            if self.center == "ACTIVE":
                # 1st CHECK FOR ACTIVE ELEMENT
                try:
                    active = bm.select_history[-1]
                except IndexError:
                    self.report({"INFO"}, "Mouse Flip: No Active Element?")
                    return {'CANCELLED'}

                # CHECK FOR UNLINKED ACTIVE ELEMENT (just use for center)
                sel_verts = [v for v in bm.verts if v.select]
                if sel_mode[0]:
                    active_verts = [active]
                else:
                    active_verts = active.verts[:]

                sel_islands = get_islands(bm, sel_verts)
                if len(sel_islands) > 1:
                    for island in sel_islands:
                        if active_verts[0] in island and len(island) == len(active_verts):
                            sel_islands.remove(island)
                            active.select = False
                        bmesh.update_edit_mesh(mesh, True)
                        sel_verts = list(flatten(sel_islands))

                # SELECTION MODES PROCESSING
                if sel_mode[0]:
                    vpos = obj_mtx @ active.co

                elif sel_mode[1]:
                    bm.faces.ensure_lookup_table()
                    ns = []
                    for p in active.link_faces:
                        n = correct_normal(obj_mtx, p.normal)
                        ns.append(n)
                    n = average_vector(ns)
                    t = Vector((obj_mtx @ active_verts[0].co) - (obj_mtx @ active_verts[1].co)).normalized()
                    om = rotation_from_vector(n, t).to_3x3()
                    scale_value = (1, 1, -1)


                elif sel_mode[2]:
                    n = correct_normal(obj_mtx, active.normal)
                    t = correct_normal(obj_mtx, active.calc_tangent_edge_pair())
                    om = rotation_from_vector(n, t).to_3x3()
                    scale_value = (1, 1, -1)

                # SET CENTER - get BBOX
                if not self.use_center:
                    vcos = [obj_mtx @ v.co for v in sel_verts]
                    avg_pos = average_vector(vcos)
                else:
                    vcos = [obj_mtx @ v.co for v in sel_verts]
                    avg_pos = average_vector([v.co for v in active_verts])
                    avg_pos = obj_mtx @ avg_pos


            elif self.center == "CURSOR":
                cursor = context.scene.cursor
                avg_pos = cursor.location
                om = cursor.rotation_quaternion.to_matrix()
                if not sum([sum(i) for i in om]) == 3.0 :
                    scale_value = (1, 1, -1)

                sel_verts = [v for v in bm.verts if v.select]
                vcos = [obj_mtx @ v.co for v in sel_verts]
                vpos = average_vector(vcos)

            else:
                # BBOX
                sel_verts = [v for v in bm.verts if v.select]
                vcos = [obj_mtx @ v.co for v in sel_verts]
                vpos = average_vector(vcos)
                avg_pos = vpos
                self.use_center = False


        else:  # OBJECT MODE
            vpos = obj.location

            if self.center == "CURSOR":
                cursor = context.scene.cursor
                avg_pos = cursor.location
                om = cursor.rotation_quaternion.to_matrix()
                if not sum([sum(i) for i in om]) == 3.0 :
                    scale_value = (1, 1, -1)

            elif self.center == "ACTIVE":
                avg_pos = (0,0,0)
            else:
                avg_pos = vpos
                self.use_center = False

            vcos = [obj_mtx @ Vector(i) for i in obj.bound_box]


        if not scale_value:
            # GET SCREEN POS
            vscreenpos = region_2d_to_location_3d(context.region, context.space_data.region_3d, self.mouse_pos, vpos)

            # GET AXIS
            x, y, z = vscreenpos[0] - vpos[0], vscreenpos[1] - vpos[1], vscreenpos[2] - vpos[2]
            axis_dict = {'X':abs(x), 'Y':abs(y), 'Z':abs(z)}
            pick_axis = sorted(axis_dict, key=axis_dict.__getitem__)[-1]

            # BBOX
            x = [co[0] for co in vcos]
            x.sort()
            y = [co[1] for co in vcos]
            y.sort()
            z = [co[2] for co in vcos]
            z.sort()
            bb_min = [x[0], y[0], z[0]]
            bb_max = [x[-1], y[-1], z[-1]]

            if pick_axis == "Y":
                scale_value = (1, -1, 1)
                if not self.use_center:
                    if vscreenpos[1] > vpos[1]:
                        # print ("Y+")
                        avg_pos = bb_max
                    else:
                        # print ("Y-")
                        avg_pos = bb_min

            elif pick_axis == "Z":
                scale_value = (1, 1, -1)
                if not self.use_center:
                    if vscreenpos[2] > vpos[2]:
                        # print ("Z+")
                        avg_pos = bb_max
                    else:
                        # print ("Z-")
                        avg_pos = bb_min
            else:
                scale_value = (-1, 1, 1)
                if not self.use_center:
                    if vscreenpos[0] > vpos[0]:
                        # print ("X+")
                        avg_pos = bb_max
                    else:
                        # print ("X-")
                        avg_pos = bb_min

        if self.center == "ACTIVE" and context.object.data.is_editmode:
            bpy.ops.mesh.duplicate(mode=1)

        bpy.ops.transform.resize(value=scale_value, orient_type='GLOBAL',
                                 orient_matrix= om,
                                 orient_matrix_type='GLOBAL', constraint_axis=(False, False, False), mirror=False,
                                 use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0,
                                 use_proportional_connected=False, use_proportional_projected=False, snap=False,
                                 snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False,
                                 snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, texture_space=False,
                                 remove_on_cancel=False, center_override=avg_pos, release_confirm=False,
                                 use_accurate=False)

        if context.object.data.is_editmode:
            bpy.ops.mesh.normals_make_consistent(inside=False)
        else:
            bpy.context.scene.tool_settings.transform_pivot_point = og_pivot
            bpy.ops.transform.select_orientation(orientation=og_orientation)
        return {'FINISHED'}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    VIEW3D_OT_ke_mouse_mirror,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
