import bmesh
import bpy
from bpy.types import Operator
from mathutils import Vector
from .._utils import (
    get_prefs,
    rotation_from_vector,
    mouse_raycast,
    correct_normal,
    average_vector,
    tri_points_order,
    vertloops,
    flatten,
    get_face_islands
)


def set_cursor(rotmat, pos=None):
    q = rotmat.to_euler("XYZ")
    bpy.context.scene.cursor.rotation_mode = "XYZ"
    bpy.context.scene.cursor.rotation_euler = q
    crot = bpy.context.scene.cursor.rotation_euler
    crot.x = round(crot.x, 4)
    crot.y = round(crot.y, 4)
    crot.z = round(crot.z, 4)
    if pos is not None:
        bpy.context.scene.cursor.location = pos
    else:
        bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.transform.select_orientation(orientation="CURSOR")
    bpy.context.tool_settings.transform_pivot_point = "CURSOR"


def set_custom_orientation(context, pos):
    try:
        bpy.ops.transform.create_orientation(name='keTF', use_view=False, use=True, overwrite=True)
        tm = context.scene.transform_orientation_slots[0].custom_orientation.matrix.copy()
        bpy.ops.transform.delete_orientation()
        set_cursor(tm, pos)
    except RuntimeError:
        # print("Fallback: Invalid selection for Orientation - just snapping to selection")
        return False
    return True


class KeCursorFitAlign(Operator):
    bl_idname = "view3d.cursor_fit_selected_and_orient"
    bl_label = "Cursor Fit & Align"
    bl_description = "Snap Cursor to selected + orient to FACE/VERT/EDGE normal. \n" \
                     "No selection = Cursor reset\n" \
                     "Object mode: Mouse over object places Cursor on face center OR\n" \
                     "Obj selected and mouse over nothing, matches obj rot/loc."
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'REGISTER'}

    cursor_orient_set = True
    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        k = get_prefs()
        og_cursor_setting = str(context.scene.cursor.rotation_mode)
        self.cursor_orient_set = k.cursorfit
        scale_check = True

        # GRAB CURRENT ORIENT & PIVOT (to restore at the end)
        og_orientation = str(context.scene.transform_orientation_slots[0].type)
        og_pivot = str(context.scene.tool_settings.transform_pivot_point)

        if context.object:
            if round(sum(context.object.scale), 6) % 3 != 0:
                scale_check = False

        if context.object and context.object.type in {'CURVE', 'GPENCIL'}:
            obj_mtx = context.object.matrix_world
            cos = []

            if context.object.type == "CURVE":
                if context.object.data.splines:
                    for s in context.object.data.splines:
                        if s.type == 'BEZIER':
                            for p in s.bezier_points:
                                if p.select_control_point:
                                    cos.append(obj_mtx @ p.co)
                        if s.type == 'NURBS':
                            for p in s.points:
                                co = p.co.copy()
                                co.resize_3d()
                                if p.select:
                                    cos.append(obj_mtx @ co)

            if context.object.type == "GPENCIL":
                for gplayer in context.object.data.layers:
                    for frame in gplayer.frames:
                        for stroke in frame.strokes:
                            for p in stroke.points:
                                if p.select:
                                    cos.append(obj_mtx @ p.co)

            if len(cos) > 1:
                n = Vector(cos[0] - cos[-1]).normalized()
                z = n.cross(Vector((0, 0, 1)))
                t_v = n.cross(z)
                if t_v.dot(n) < 0.00001:
                    y = n.cross(Vector((0, 1, 0)))
                    t_v = n.cross(y)
                rot_mtx = rotation_from_vector(n, t_v)
                set_cursor(rot_mtx)
            elif cos:
                bpy.ops.view3d.snap_cursor_to_selected()
            else:
                bpy.ops.view3d.snap_cursor_to_center()

            # Bleh
            if cos and context.object.type == "GPENCIL":
                bpy.ops.gpencil.snap_cursor_to_selected()

        elif context.mode == "EDIT_MESH":
            sel_mode = context.tool_settings.mesh_select_mode[:]
            obj = context.edit_object
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

            ps = [v.co for v in sel_verts]
            pos = obj_mtx @ average_vector(ps)
            using_default = True

            #
            # POLY MODE
            #
            if sel_mode[2]:
                sel_poly = [p for p in bm.faces if p.select]

                if sel_poly:

                    af = bm.faces.active
                    if af not in sel_poly:
                        af = sel_poly[-1]

                    if len(sel_poly) == 1:
                        pos = obj_mtx @ bm.faces[af.index].calc_center_median()

                    sel_islands = get_face_islands(bm, sel_verts)

                    if len(sel_islands) > 1:
                        normal = correct_normal(obj_mtx, af.normal)
                        tangent = correct_normal(obj_mtx, af.calc_tangent_edge_pair().normalized())
                        # fallbacks (tangent edges are same as n on other face etc.)
                        if normal.magnitude == 0 or tangent.magnitude == 0:
                            normal = Vector((0, 0, 1))
                            tangent = Vector((1, 0, 0))
                        rot_mtx = rotation_from_vector(normal, tangent, rw=True)
                        set_cursor(rot_mtx, pos=pos)
                    else:
                        using_default = set_custom_orientation(context, pos)
                        if not using_default:
                            bpy.ops.view3d.snap_cursor_to_selected()
                else:
                    bpy.ops.view3d.snap_cursor_to_center()

                vert_mode = False
            #
            # EDGE MODE
            #
            if sel_mode[1]:
                n = Vector((0, 0, 1))
                t_v = Vector((1, 0, 0))

                loop_mode = False
                line_mode = False

                sel_edges = [e for e in bm.edges if e.select]
                e_count = len(sel_edges)

                if e_count > 1:
                    vps = [e.verts[:] for e in sel_edges]
                    loops = vertloops(vps)
                    if len(loops) >= 1 and loops[0][0] != loops[0][-1]:
                        fl = list(set(flatten(vps)))
                        if len(fl) == len(loops[0]):
                            line_mode = True
                            using_default = False

                if not line_mode:
                    using_default = set_custom_orientation(context, pos)
                    vert_mode = False

                if not using_default:
                    # todo: clean up redundant code
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

                        n = Vector((ev[0].normal + ev[1].normal) * .5).normalized()
                        t_v = Vector((etv[0].normal + etv[1].normal) * .5).normalized()

                        if abs(round(n.dot(t_v), 2)) == 1 or shared_face or line_mode:
                            avg_v, avg_e = [], []
                            for e in sel_edges:
                                avg_v.append((e.verts[0].normal + e.verts[1].normal) * .5)
                                uv = Vector(e.verts[0].co - e.verts[1].co).normalized()
                                avg_e.append(uv)

                            n = average_vector(avg_v)
                            # I forgot why I needed these checks?
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

            #
            # VERT (& GENERAL AVERAGE) MODE
            #
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
                                t_c = Vector((1, 0, 0))
                                n = Vector((0, 0, 1))
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
                bmesh.update_edit_mesh(obj.data)

        #
        # OBJECT MODE
        #
        elif context.mode == "OBJECT":

            sel_obj = [o for o in context.selected_objects]
            active_object = context.active_object if context.active_object in sel_obj else None
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)
            nohitsel = True if hit_obj not in sel_obj else False

            # excluding if any modifier that deform/ change the mesh's location to avoid any None type error
            # contrib: Wahyu Nugraha
            m_deform = ['ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM',
                        'SHRINKWRAP',
                        'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP',
                        'WAVE']

            if hit_normal and hit_obj:
                mfs = []
                # Terrible workaround for raycast index issue
                if len(hit_obj.modifiers) > 0:
                    for m in hit_obj.modifiers:
                        if m.show_viewport and m.type not in m_deform:
                            mfs.append(m)
                            m.show_viewport = False
                    # casting again for unevaluated index (the "proper way" is bugged?)
                    hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos)

                obj_mtx = hit_obj.matrix_world.copy()

                if round(sum(hit_obj.scale), 6) % 3 != 0:
                    scale_check = False
                else:
                    scale_check = True

                bm = bmesh.new()
                bm.from_mesh(hit_obj.data)
                bm.faces.ensure_lookup_table()

                normal = bm.faces[hit_face].normal
                tangent = bm.faces[hit_face].calc_tangent_edge()
                pos = obj_mtx @ bm.faces[hit_face].calc_center_median()

                rot_mtx = rotation_from_vector(normal, tangent, rw=True)
                rot_mtx = obj_mtx @ rot_mtx
                set_cursor(rot_mtx, pos=pos)

                if mfs:
                    for m in mfs:
                        m.show_viewport = True

            elif len(sel_obj) == 1 and nohitsel:
                # LOC - as bo
                context.scene.cursor.location = sel_obj[0].matrix_world.to_translation()
                # ROT - as obj
                context.scene.cursor.rotation_euler = sel_obj[0].matrix_world.to_euler()
                if self.cursor_orient_set:
                    bpy.ops.transform.select_orientation(orientation="CURSOR")
                    context.tool_settings.transform_pivot_point = "CURSOR"

            elif len(sel_obj) == 2 and nohitsel:
                # LOC
                context.scene.cursor.location = average_vector([o.matrix_world.to_translation() for o in sel_obj])
                # ROT - towards active
                if active_object is not None:
                    if sel_obj[0] == active_object:
                        target, start = active_object, sel_obj[-1]
                    else:
                        target, start = active_object, sel_obj[0]
                else:
                    start, target = sel_obj[0], sel_obj[-1]
                v = Vector(target.matrix_world.to_translation() - start.matrix_world.to_translation()).normalized()
                if round(abs(v.dot(Vector((1, 0, 0)))), 3) == 1:
                    u = Vector((0, 0, 1))
                else:
                    u = Vector((-1, 0, 0))
                t = v.cross(u).normalized()
                rot_mtx = rotation_from_vector(v, t, rw=False)
                context.scene.cursor.rotation_euler = rot_mtx.to_euler()

            elif len(sel_obj) >= 3 and nohitsel:
                # LOC
                context.scene.cursor.location = average_vector([o.matrix_world.to_translation() for o in sel_obj])
                # ROT - as active
                if active_object:
                    context.scene.cursor.rotation_euler = active_object.matrix_world.to_euler()
                else:
                    context.scene.cursor.rotation_euler = sel_obj[-1].matrix_world.to_euler()
            else:
                bpy.ops.view3d.snap_cursor_to_center()

        if not self.cursor_orient_set:
            # RESET OP TRANSFORMS
            bpy.ops.transform.select_orientation(orientation=og_orientation)
            context.scene.tool_settings.transform_pivot_point = og_pivot

        if og_cursor_setting != "QUATERNION":
            # just going to go ahead and assume no one uses this as default, for back-compatibility reasons...
            context.scene.cursor.rotation_mode = og_cursor_setting
        else:
            context.scene.cursor.rotation_mode = 'XYZ'

        if not scale_check:
            self.report({"INFO"}, "Object Scale is not applied")

        return {'FINISHED'}
