bl_info = {
    "name": "Fit Cursor to Selected & Orient",
    "author": "Kjell Emanuelsson 2020",
    "category": "Modeling",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 4, 0),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from mathutils import Vector
from .ke_utils import rotation_from_vector, mouse_raycast, correct_normal, average_vector, \
    tri_points_order, get_loops, flatten


def set_cursor(rotmat, pos=[]):
    q = rotmat.to_quaternion()
    bpy.context.scene.cursor.rotation_mode = "QUATERNION"
    bpy.context.scene.cursor.rotation_quaternion = q
    if pos:
        bpy.context.scene.cursor.location = pos
    else:
        bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.transform.select_orientation(orientation="CURSOR")
    bpy.context.tool_settings.transform_pivot_point = "CURSOR"


class VIEW3D_OT_cursor_fit_selected_and_orient(bpy.types.Operator):
    bl_idname = "view3d.cursor_fit_selected_and_orient"
    bl_label = "Cursor snap to selected and orient"
    bl_description = "Snap Cursor to selected + orient to FACE/VERT/EDGE normal. No selection = Cursor reset " \
                     "Note: Works with mouse over on faces in Object mode."
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    cursorOP = True
    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        og_cursor_setting = str(context.scene.cursor.rotation_mode)
        self.cursorOP = bpy.context.scene.kekit.cursorfit

        if not self.cursorOP:
            # GRAB CURRENT ORIENT & PIVOT (to restore at the end)
            og_orientation = str(bpy.context.scene.transform_orientation_slots[0].type)
            og_pivot = str(bpy.context.scene.tool_settings.transform_pivot_point)

        if bpy.context.mode == "EDIT_MESH":
            sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
            obj = bpy.context.edit_object
            obj_mtx = obj.matrix_world.copy()
            bm = bmesh.from_edit_mesh(obj.data)

            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            vert_mode = True
            sel_verts = [v for v in bm.verts if v.select]
            sel_count = len(sel_verts)

            if sel_count == 0:
                bpy.ops.view3d.snap_cursor_to_center()
                return {'FINISHED'}

            # POLY MODE -----------------------------------------------------------------------
            if sel_mode[2]:
                sel_poly = [p for p in bm.faces if p.select]

                if sel_poly:

                    # sel_islands = get_islands(bm, sel_verts)

                    v_normals = [p.normal for p in sel_poly]
                    v_tan = [p.calc_tangent_edge_pair() for p in sel_poly]
                    face = sel_poly[-1]

                    normal = correct_normal(obj_mtx, sum(v_normals, Vector()) / len(v_normals))
                    tangent = correct_normal(obj_mtx, sum(v_tan, Vector()) / len(v_tan))

                    if len(sel_poly) == 1:
                        pos = obj_mtx @ bm.faces[face.index].calc_center_median()
                    else:
                        ps = [v.co for v in sel_verts]
                        pos = obj_mtx @ average_vector(ps)

                    # fallback for all faces selected type of scenarios
                    if sum(normal) == 0:
                        normal = Vector((0,0,1))
                        tangent = Vector((1,0,0))

                    rot_mtx = rotation_from_vector(normal, tangent, rw=False)
                    set_cursor(rot_mtx, pos=pos)

                else:
                    bpy.ops.view3d.snap_cursor_to_center()

                vert_mode = False


            # EDGE MODE -----------------------------------------------------------------------
            if sel_mode[1]:

                loop_mode = False
                line_mode = False

                sel_edges = [e for e in bm.edges if e.select]
                e_count = len(sel_edges)

                if e_count > 1:
                    vps = [e.verts[:] for e in sel_edges]
                    loops = get_loops(vps, legacy=True)
                    if len(loops) >= 1 and loops[0][0] != loops[0][-1]:
                        fl = list(set(flatten(vps)))
                        if len(fl) == len(loops[0]):
                            line_mode = True

                if e_count == 1:

                    ev = sel_edges[0].verts[:]
                    n = Vector((ev[0].normal + ev[1].normal) * .5).normalized()
                    t_v = Vector((ev[0].co - ev[1].co).normalized())
                    vert_mode = False

                elif e_count == 2 or line_mode:
                    shared_face = []
                    for f in sel_edges[0].link_faces:
                        for fe in sel_edges[1].link_faces:
                            if fe == f:
                                shared_face = f
                                break

                    ev = sel_edges[0].verts[:]
                    etv = sel_edges[1].verts[:]

                    n = Vector((ev[0].normal + ev[1].normal)*.5).normalized()
                    t_v = Vector((etv[0].normal + etv[1].normal)*.5).normalized()

                    if abs(round(n.dot(t_v),2)) == 1 or shared_face or line_mode:
                        avg_v, avg_e = [], []
                        for e in sel_edges:
                            avg_v.append((e.verts[0].normal + e.verts[1].normal) * .5)
                            uv = Vector(e.verts[0].co - e.verts[1].co).normalized()
                            avg_e.append(uv)

                        n = average_vector(avg_v)
                        # I forgot why i needed these checks?
                        if sum(n) == 0:
                            n = avg_v[0]
                        t_v = average_vector(avg_e)
                        if sum(t_v) == 0:
                            t_v = avg_e[0]

                        if shared_face:
                            t_v = avg_e[0]

                        vert_mode = False


                elif e_count > 2:
                    loop_mode = True

                    startv = Vector(sel_edges[0].verts[0].co - sel_edges[0].verts[1].co).normalized()
                    cv1 = Vector(sel_edges[1].verts[0].co - sel_edges[1].verts[1].co).normalized()
                    cdot = abs(round(startv.dot(cv1), 6))

                    for e in sel_edges[2:]:
                        v = Vector(e.verts[0].co - e.verts[1].co).normalized()
                        vdot = abs(round(startv.dot(v), 3))
                        if vdot < cdot:
                            cv1 = v
                            cdot = vdot

                    n = startv
                    t_v = cv1
                    n.negate()
                    vert_mode = False

                # final pass
                n = correct_normal(obj_mtx, n)
                t_v = correct_normal(obj_mtx, t_v)
                n = n.cross(t_v)

                # vert average fallback
                if sum(t_v) == 0 or sum(n) == 0:
                    vert_mode = True

                if not vert_mode:
                    if loop_mode:
                        rot_mtx = rotation_from_vector(n, t_v, rotate90=True)
                    else:
                        rot_mtx = rotation_from_vector(n, t_v, rotate90=False)

                    set_cursor(rot_mtx)


            # VERT (& GENERAL AVERAGE) MODE -----------------------------------------------------------------------
            if sel_mode[0] or vert_mode:

                if sel_count == 2:
                    n = Vector(sel_verts[0].co - sel_verts[1].co).normalized()
                    v_n = [v.normal for v in sel_verts]
                    t_v = correct_normal(obj_mtx, sum(v_n, Vector()) / len(v_n))
                    n = correct_normal(obj_mtx, n)
                    t_v = t_v.cross(n)

                    rot_mtx = rotation_from_vector(n, t_v)
                    set_cursor(rot_mtx)

                elif sel_count == 3:
                    cv = [v.co for v in sel_verts]

                    # make triangle vectors, sort to avoid the hypot.vector
                    h = tri_points_order(cv)
                    tri = sel_verts[h[0]].co, sel_verts[h[1]].co, sel_verts[h[2]].co
                    v1 = Vector((tri[0] - tri[1])).normalized()
                    v2 = Vector((tri[0] - tri[2])).normalized()
                    v1 = correct_normal(obj_mtx, v1)
                    v2 = correct_normal(obj_mtx, v2)
                    n_v = v1.cross(v2)

                    # flipcheck
                    v_n = [v.normal for v in sel_verts]
                    ncheck = correct_normal(obj_mtx, sum(v_n, Vector()) / len(v_n))
                    if ncheck.dot(n_v) < 0:
                        n_v.negate()

                    # tangentcheck
                    c1 = n_v.cross(v1).normalized()
                    c2 = n_v.cross(v2).normalized()
                    if c1.dot(n_v) > c2.dot(n_v):
                        u_v = c2
                    else:
                        u_v = c1
                    t_v = u_v.cross(n_v).normalized()

                    rot_mtx = rotation_from_vector(n_v, t_v)
                    set_cursor(rot_mtx)

                elif sel_count != 0:

                    v_n = [v.normal for v in sel_verts]
                    n = correct_normal(obj_mtx, sum(v_n, Vector()) / len(v_n))

                    if sel_count >= 1:
                        if sel_count == 1:
                            if not sel_verts[0].link_edges:
                                # floater vert check -> world rot
                                t_c = Vector((1,0,0))
                                n = Vector((0,0,1))
                            else:
                                t_c = sel_verts[0].co - sel_verts[0].link_edges[0].other_vert(sel_verts[0]).co
                        else:
                            t_c = sel_verts[0].co - sel_verts[1].co

                        t_c = correct_normal(obj_mtx, t_c)
                        t_v = n.cross(t_c).normalized()

                        rot_mtx = rotation_from_vector(n, t_v)
                        set_cursor(rot_mtx)

                elif sel_count == 0:
                    bpy.ops.view3d.snap_cursor_to_center()

                bm.select_flush_mode()
                bmesh.update_edit_mesh(obj.data, True)

        # OBJECT MODE -----------------------------------------------------------------------
        elif bpy.context.mode == "OBJECT":
            sel_obj = [o for o in context.selected_objects]
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

            if hit_normal and hit_obj:
                obj_mtx = hit_obj.matrix_world.copy()

                bm = bmesh.new()
                bm.from_mesh(hit_obj.data)
                bm.faces.ensure_lookup_table()

                normal = bm.faces[hit_face].normal
                tangent = bm.faces[hit_face].calc_tangent_edge_pair()
                pos = obj_mtx @ bm.faces[hit_face].calc_center_median()

                rot_mtx = rotation_from_vector(normal, tangent, rw=False)
                rot_mtx = obj_mtx @ rot_mtx
                set_cursor(rot_mtx, pos=pos)

            elif sel_obj and not hit_normal:
                context.scene.cursor.location = sel_obj[0].location
                context.scene.cursor.rotation_euler = sel_obj[0].rotation_euler

            else:
                bpy.ops.view3d.snap_cursor_to_center()


        if not self.cursorOP:
            # RESET OP TRANSFORMS
            bpy.ops.transform.select_orientation(orientation=og_orientation)
            bpy.context.scene.tool_settings.transform_pivot_point = og_pivot

        if og_cursor_setting != "QUATERNION":
            # just gonna go ahead and assume no one uses this as default, for back-compatibility reasons...
            context.scene.cursor.rotation_mode = og_cursor_setting
        else:
            context.scene.cursor.rotation_mode = 'XYZ'


        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
           VIEW3D_OT_cursor_fit_selected_and_orient,
           )

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
