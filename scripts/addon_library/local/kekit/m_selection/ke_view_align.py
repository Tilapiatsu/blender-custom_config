import bmesh
from bpy.types import Operator
from mathutils import Vector, Matrix
from .._utils import correct_normal, average_vector, get_distance


def sort_vert_order(vcoords):
    sq = False
    vp = vcoords[0], vcoords[1], vcoords[2]
    vp1 = get_distance(vp[0], vp[1])
    vp2 = get_distance(vp[0], vp[2])
    vp3 = get_distance(vp[1], vp[2])
    if round(vp1, 4) == round(vp2, 4):
        sq = True
    vpsort = {"2": vp1, "1": vp2, "0": vp3}
    s = [int(i) for i in sorted(vpsort, key=vpsort.__getitem__)]
    s.reverse()
    return [vcoords[s[0]], vcoords[s[1]], vcoords[s[2]]], sq


class KeViewAlign(Operator):
    bl_idname = "view3d.ke_view_align"
    bl_label = "View Align Selected"
    bl_description = "Align View to Active Face or 3 vertices."
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode and
                context.space_data.type == "VIEW_3D")

    def execute(self, context):
        # SETUP & SELECTIONS
        w = Vector((0, 0, 1))
        rv3d = context.space_data.region_3d
        sel_mode = context.tool_settings.mesh_select_mode[:]

        o = context.object
        obj_mtx = o.matrix_world

        bm = bmesh.from_edit_mesh(o.data)
        active = bm.faces.active
        face_mode = False
        if active and sel_mode[2]:
            if len(active.verts) == 3:
                sel_verts = active.verts[:]
            else:
                sel_verts = active.verts[:]
                face_mode = True
        else:
            sel_poly = [p for p in bm.faces if p.select]
            if sel_poly:
                sel_verts = [v for v in sel_poly[0].verts]
            else:
                sel_verts = [v for v in bm.verts if v.select]

        if not sel_verts or len(sel_verts) < 3:
            self.report(type={'INFO'}, message="Nothing selected?")
            return {'CANCELLED'}

        if face_mode:
            n = correct_normal(obj_mtx, active.normal)
            t = correct_normal(obj_mtx, active.calc_tangent_edge())

            c = t.cross(w)
            if c.dot(n) < 0:
                t.negate()
            b = n.cross(t).normalized()

            unrotated = Matrix((t, b, n)).to_4x4().inverted().to_quaternion()
            avg_pos = obj_mtx @ active.calc_center_median()

        else:
            # SORT 3 VERTICES ORDER FOR BEST ANGLES FOR TANGENT & BINORMAL (Disregard hypothenuse)
            vec_poslist_sort = sort_vert_order([sel_verts[0].co, sel_verts[1].co, sel_verts[2].co])
            vec_poslist = vec_poslist_sort[0]
            p1, p2, p3 = obj_mtx @ vec_poslist[0], obj_mtx @ vec_poslist[1], obj_mtx @ vec_poslist[2]
            v_1 = p2 - p1
            v_2 = p3 - p1

            # If square, switch t & b
            if vec_poslist_sort[1]:
                t1 = v_1.dot(w)
                t2 = v_2.dot(w)
                if t2 > t1:
                    v_1, v_2 = v_2, v_1
            else:
                v_1.negate()

            n = v_1.cross(v_2).normalized()

            # n direction flip check
            fn = average_vector([v.normal for v in sel_verts])
            fn = correct_normal(obj_mtx, fn)

            check = n.dot(fn.normalized())
            if check <= 0:
                n.negate()
                v_1.negate()
                v_2.negate()

            # additional direction check to avoid some rotation issues
            if v_1.dot(w) < 0:
                v_1.negate()

            # CREATE VIEW ROTATION & LOCATION & APPLY
            avg_pos = obj_mtx @ average_vector(vec_poslist)
            b = v_1.cross(n).normalized()
            unrotated = Matrix((b, v_1, n)).to_4x4().inverted().to_quaternion()

        rv3d.view_rotation = unrotated
        rv3d.view_location = avg_pos

        bmesh.update_edit_mesh(o.data)

        return {'FINISHED'}
