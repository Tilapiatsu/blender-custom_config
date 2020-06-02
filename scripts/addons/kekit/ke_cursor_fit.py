bl_info = {
    "name": "Fit Cursor to Selected & Orient",
    "author": "Kjell Emanuelsson 2020",
    "category": "Modeling",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from mathutils import Vector
from .ke_utils import rotation_from_vector, mouse_raycast, correct_normal, average_vector


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

    mouse_pos = Vector((0, 0))

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
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

                    rot_mtx = rotation_from_vector(normal, tangent, rw=False)
                    set_cursor(rot_mtx, pos=pos)

                else:
                    bpy.ops.view3d.snap_cursor_to_center()

                vert_mode = False

            # EDGE MODE -----------------------------------------------------------------------
            if sel_mode[1]:
                sel_edges = [e for e in bm.edges if e.select]

                shared_face = []
                if len(sel_edges) == 2:
                    for f in sel_edges[0].link_faces:
                        for fe in sel_edges[1].link_faces:
                            if fe == f:
                                shared_face = f
                                break

                avg_v, avg_e = [], []
                for e in sel_edges:
                    avg_v.append((e.verts[0].normal + e.verts[1].normal)*.5)
                    uv = Vector(e.verts[0].co - e.verts[1].co).normalized()
                    avg_e.append(uv)

                n = average_vector(avg_v)
                if sum(n) == 0:
                    print("zero n")
                    n = avg_v[0]
                t_v = average_vector(avg_e)
                if sum(t_v) == 0:
                    print("zero e")
                    t_v = avg_e[0]

                if shared_face:
                    t_v = avg_e[0]

                n = correct_normal(obj_mtx, n)
                t_v = correct_normal(obj_mtx, t_v)
                n = n.cross(t_v)

                rot_mtx = rotation_from_vector(n, t_v, rotate90=False)
                set_cursor(rot_mtx)

                vert_mode = False


            # VERT (& GENERAL AVERAGE) MODE -----------------------------------------------------------------------
            if sel_mode[0] or vert_mode:
                print("VERTMODE")

                if sel_count == 2:
                    n = Vector(sel_verts[0].co - sel_verts[1].co).normalized()
                    v_n = [v.normal for v in sel_verts]
                    t_v = correct_normal(obj_mtx, sum(v_n, Vector()) / len(v_n))
                    n = correct_normal(obj_mtx, n)
                    t_v = t_v.cross(n)

                    rot_mtx = rotation_from_vector(n, t_v)
                    set_cursor(rot_mtx)

                elif sel_count != 0:

                    v_n = [v.normal for v in sel_verts]
                    n = correct_normal(obj_mtx, sum(v_n, Vector()) / len(v_n))

                    if sel_count >= 1:
                        if sel_count == 1:
                            t_c = sel_verts[0].co - sel_verts[0].link_edges[-1].other_vert(sel_verts[0]).co
                        else:
                            t_c = sel_verts[0].co - sel_verts[1].co

                        t_c = correct_normal(obj_mtx, t_c)
                        t_v = n.cross(t_c).normalized()

                        rot_mtx = rotation_from_vector(n, t_v)
                        set_cursor(rot_mtx)

                elif sel_count == 0:
                    bpy.ops.view3d.snap_cursor_to_center()

        # OBJECT MODE -----------------------------------------------------------------------
        elif bpy.context.mode == "OBJECT":
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

            else:
                bpy.ops.view3d.snap_cursor_to_center()

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
