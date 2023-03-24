import bpy
import bmesh
from bpy.types import Operator
from mathutils import Vector, Matrix, Quaternion
from math import copysign
from ._utils import get_selected, correct_normal, average_vector, get_distance


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
    bl_options = {'REGISTER', 'UNDO'}

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


class KeViewAlignToggle(Operator):
    bl_idname = "view3d.ke_view_align_toggle"
    bl_label = "View Align Selected Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    mode : bpy.props.EnumProperty(
        items=[("SELECTION", "", "", 1),
               ("CURSOR", "", "", 2),
               ],
        name="View Align Mode",
        default="SELECTION")

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "SELECTION":
            return "Align View to Active Face OR 3 Vertices OR 2 Edges (or, in Object-mode: Obj's Z axis)\n" \
                   "Toggle (run again) to restore view from before alignment"
        else:
            return "Align View to Cursor Z-Axis Orientation\n" \
                   "Toggle (run again) to restore view from before alignment"

    def execute(self, context):
        rv3d = context.space_data.region_3d
        v = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        slot = context.scene.kekit_temp.viewtoggle
        # SET
        if sum(slot) == 0:
            p = [int(rv3d.is_perspective)]
            d = [rv3d.view_distance]
            loc = [i for i in rv3d.view_location]
            rot = [i for i in rv3d.view_rotation]
            v = p + d + loc + rot
            slot[0] = v[0]
            slot[1] = v[1]
            slot[2] = v[2]
            slot[3] = v[3]
            slot[4] = v[4]
            slot[5] = v[5]
            slot[6] = v[6]
            slot[7] = v[7]
            slot[8] = v[8]

            if self.mode == "SELECTION":
                if context.object.mode == "EDIT":
                    bpy.ops.view3d.ke_view_align()
                else:
                    bpy.ops.view3d.view_axis(type='TOP', align_active=True)
                bpy.ops.view3d.view_selected(use_all_regions=False)

            elif self.mode == "CURSOR":
                q = context.scene.cursor.rotation_euler.to_quaternion()
                rv3d.view_rotation = q
                bpy.ops.view3d.view_center_cursor()

            if rv3d.is_perspective:
                bpy.ops.view3d.view_persportho()
        else:
            v[0] = slot[0]
            v[1] = slot[1]
            v[2] = slot[2]
            v[3] = slot[3]
            v[4] = slot[4]
            v[5] = slot[5]
            v[6] = slot[6]
            v[7] = slot[7]
            v[8] = slot[8]

            if not rv3d.is_perspective and bool(v[0]):
                bpy.ops.view3d.view_persportho()
            rv3d.view_distance = v[1]
            rv3d.view_location = Vector(v[2:5])
            rv3d.view_rotation = Quaternion(v[5:9])

            slot[0] = 0
            slot[1] = 0
            slot[2] = 0
            slot[3] = 0
            slot[4] = 0
            slot[5] = 0
            slot[6] = 0
            slot[7] = 0
            slot[8] = 0

        return {"FINISHED"}


class KeViewAlignSnap(Operator):
    bl_idname = "view3d.ke_view_align_snap"
    bl_label = "View Align Snap"
    bl_description = "Snap view to nearest Orthographic. Note: No toggle - just rotate view back to perspective"
    bl_options = {'REGISTER'}

    contextual: bpy.props.BoolProperty(default=False)

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


#
# CLASS REGISTRATION
#
classes = (
    KeViewAlign,
    KeViewAlignSnap,
    KeViewAlignToggle,
)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
