import bpy
import bmesh
from bpy_types import Operator
from mathutils import Vector
from ._utils import point_axis_raycast, average_vector


def zmove(value, zonly=True):
    if zonly:
        values = (0, 0, value)
    else:
        values = value
    bpy.ops.transform.translate(
        value=values, orient_type='GLOBAL',
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
        mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
        proportional_size=1, use_proportional_connected=False,
        use_proportional_projected=False, release_confirm=True)


def sort_low_z_bb(vc):
    lz = [vc[0], vc[3], vc[4], vc[7]]
    return sorted(lz, key=lambda z: z[2])


def sort_low_z(vc):
    return sorted(vc, key=lambda z: z[2])


def editmode_ctx_cos(obj, ccos):
    bm = bmesh.from_edit_mesh(obj.data)
    active = bm.select_history.active
    if active:
        if type(active).__name__ == "BMVert":
            ccos = [obj.matrix_world @ active.co]
        else:
            ccos = sort_low_z([obj.matrix_world @ v.co for v in active.verts])
    else:
        ccos = [ccos[0]]
    return ccos


class KeGround(Operator):
    bl_idname = "view3d.ke_ground"
    bl_label = "Ground (or Center)"
    bl_description = "Ground (or Center) selected Object(s), or selected elements (snap to world Z0 only)"
    bl_options = {'REGISTER', 'UNDO'}

    op: bpy.props.EnumProperty(
        items=[("GROUND", "Ground", "", 1),
               ("CENTER", "Ground Midpoint", "", 2),
               ("CENTER_GROUND", "Ground & Center XY", "", 3),
               ("CENTER_ALL", "Center XYZ", "", 4),
               ("UNDER", "Under-Ground", "", 5)],
        name="Operation",
        default="GROUND")

    group: bpy.props.EnumProperty(
        items=[("NONE", "Individual", "", 1),
               ("AVG", "Group Averaged", "", 2),
               ("CTX", "Group Active", "", 3)],
        name="Process",
        default="NONE")

    custom_z: bpy.props.FloatProperty(
        name="Ground (Z-Pos)", description="Override for custom position on the Global Z axis", default=0)

    raycast: bpy.props.BoolProperty(
        name="Raycast", description="Stops on obstructions on the way down (Nothing: Z Pos)", default=False)

    ignore_selected: bpy.props.BoolProperty(
        name="Ignore Selected", description="Ignore selected Objects when raycasting", default=False)

    sel_obj = []
    editmode = False
    ctx = None

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "op", expand=True)
        layout.prop(self, "custom_z")
        layout.separator(factor=0.5)
        layout.prop(self, "group", expand=True)
        layout.separator(factor=0.5)
        row = layout.row()
        if self.op == "CENTER_ALL":
            row.enabled = False
        row.prop(self, "raycast")
        layout.prop(self, "ignore_selected")
        layout.separator(factor=1)

    def bbcast(self, points, zs):
        hits = []
        low_bb = sort_low_z_bb(points)
        low_z = low_bb[0][2]
        for p in low_bb:
            result, hit = self.ground_raycast(low_z=low_z, point=p, zs=zs)
            if hit is not None:
                hits.append([result[0], result[-1]])
        if hits:
            return sorted(hits, key=lambda x: x[0])[0]
        return zs

    def ground_raycast(self, low_z, point, zs):
        point[2] -= 0.0001  # hack so it doesn't trace itself...
        raycast = point_axis_raycast(self.ctx, vec_point=point, axis=2)
        if raycast[1] is not None:
            hit = raycast[1]
            hit[2] -= 0.0001  # hack offset compensate
            dist = low_z - hit[2]
            zs[-1] = dist + (zs[-1] - zs[0])
            zs[0] = dist
            if zs[0] == 0:
                print("Ground: Cancelled - Raycast distance is zero")
                for ob in self.sel_obj:
                    ob.select_set(True)
                if self.ignore_selected:
                    for obj in self.sel_obj:
                        obj.hide_set(False)
                return {"CANCELLED"}
        return zs, raycast[1]

    def zmove_process(self, vc, zs):
        if self.op == "GROUND":
            zmove((round(zs[0], 6) - self.custom_z) * -1)

        elif self.op == "CENTER":
            midz = sorted([c[2] for c in vc])
            z = (midz[-1] - midz[0]) / 2
            zmove((round(z + zs[0], 6) - self.custom_z) * -1)

        elif self.op == "CENTER_ALL":
            zx = sorted([c[0] for c in vc])
            zy = sorted([c[1] for c in vc])
            xo = round(zx[0] + ((zx[-1] - zx[0]) / 2), 6) * -1
            yo = round(zy[0] + ((zy[-1] - zy[0]) / 2), 6) * -1
            zo = round(zs[0] + ((zs[-1] - zs[0]) / 2), 6) * -1
            zmove((xo, yo, zo), zonly=False)

        elif self.op == "CENTER_GROUND":
            zx = sorted([c[0] for c in vc])
            zy = sorted([c[1] for c in vc])
            xo = round(zx[0] + ((zx[-1] - zx[0]) / 2), 6) * -1
            yo = round(zy[0] + ((zy[-1] - zy[0]) / 2), 6) * -1
            zo = (round(zs[0], 6) - self.custom_z) * -1
            zmove((xo, yo, zo), zonly=False)

        elif self.op == "UNDER":
            midz = sorted([c[2] for c in vc])
            z = midz[-1] - midz[0]
            zmove(round(zs[0] + z, 6) * -1)

    def execute(self, context):
        # Prep/Selection Check
        self.sel_obj = [o for o in context.selected_objects]
        if not self.sel_obj:
            self.report({"INFO"}, "Ground: Selection Error?")
            return {'CANCELLED'}

        if context.object.type == "MESH":
            self.editmode = bool(context.object.data.is_editmode)
        else:
            self.editmode = False

        self.ctx = context
        ignore_raycast = False
        if self.op == "CENTER_ALL":
            ignore_raycast = True
            self.raycast = False

        og = context.object
        bpy.ops.object.mode_set(mode='OBJECT')

        if self.ignore_selected:
            for o in self.sel_obj:
                o.hide_set(True)

        # OBJECT MNODE + GROUP
        if not self.editmode and self.group != "NONE":
            grp_cos = []
            grp_zs = []

            # GROUP w. averaged values
            if self.group == "AVG":
                for o in self.sel_obj:
                    o.hide_set(True)
                    if og.type == "MESH":
                        grp_cos.extend([o.matrix_world @ Vector(co) for co in o.bound_box])
                    else:
                        grp_cos = [o.location] * 8
                grp_avg = average_vector(grp_cos)
                grp_cos = [grp_avg]
                grp_zs = [p[2] for p in grp_cos]
                grp_zs.sort()
                if self.raycast:
                    grp_zs, hit = self.ground_raycast(low_z=grp_cos[0][2], point=grp_cos[0], zs=grp_zs)

            # GROUP w. active(context.object) values
            elif self.group == "CTX":
                og.hide_set(True)
                if og.type == "MESH":
                    grp_cos.extend([og.matrix_world @ Vector(co) for co in og.bound_box])
                else:
                    grp_cos = [og.location] * 8
                grp_zs = [p[2] for p in grp_cos]
                grp_zs.sort()
                if self.raycast:
                    grp_zs = self.bbcast(points=grp_cos, zs=grp_zs)

            for o in self.sel_obj:
                # hiding from raycast - need superflous select_set or 'unhiding' won't work!?
                o.hide_set(False)
                o.select_set(True)

            self.zmove_process(vc=grp_cos, zs=grp_zs)

        else:
            # INDIVIDUALLY Process each Object / Edit Mode Element selected
            bpy.ops.object.select_all(action="DESELECT")

            for o in self.sel_obj:

                if self.ignore_selected:
                    o.hide_set(False)
                o.select_set(True)
                context.view_layer.objects.active = o

                sel_verts = [v for v in o.data.vertices if v.select] if self.editmode else []

                if sel_verts:
                    cos = [o.matrix_world @ v.co for v in sel_verts]
                    zs = [p[2] for p in cos]
                    zs.sort()

                    if self.raycast:
                        if self.group == "NONE":
                            # raycast each vert
                            zs = []
                            for co in cos:
                                zs.append(self.ground_raycast(low_z=co[2], point=co, zs=[co[2], co[2]])[0][0])

                        elif self.group == "CTX":
                            # raycast verts to active verts z (fallback random)
                            bpy.ops.object.mode_set(mode='EDIT')
                            cos = editmode_ctx_cos(o, cos)

                            bpy.ops.object.mode_set(mode='OBJECT')
                            z, hit = self.ground_raycast(low_z=cos[0][2], point=cos[0], zs=[cos[0][2], cos[0][2]])
                            zs = [z[0]] * len(sel_verts)

                        elif self.group == "AVG":
                            cos = [average_vector(cos)]
                            z, hit = self.ground_raycast(low_z=cos[0][2], point=cos[0], zs=[cos[0][2], cos[0][2]])
                            zs = [z[0]] * len(sel_verts)

                        # bmesh move verts
                        bpy.ops.object.mode_set(mode='EDIT')
                        mesh = o.data
                        bm = bmesh.from_edit_mesh(mesh)
                        bm.verts.ensure_lookup_table()
                        sel_verts = [v for v in bm.verts if v.select]
                        for v, z in zip(sel_verts, zs):
                            co = o.matrix_world @ v.co
                            co[2] -= round(z, 6)
                            v.co = o.matrix_world.inverted() @ co

                        bmesh.update_edit_mesh(mesh)
                        mesh.update()
                        zs = [0, 0]
                    else:
                        bpy.ops.object.mode_set(mode='EDIT')
                        if self.group == "CTX":
                            cos = editmode_ctx_cos(o, cos)
                            zs = [p[2] for p in cos]
                        elif self.group == "AVG":
                            grp_avg = average_vector(cos)
                            cos = [grp_avg]
                            zs = [p[2] for p in cos]
                            zs.sort()

                    # Process
                    self.zmove_process(cos, zs)

                else:
                    # OBJECT MODE - Non-grouped
                    if og.type == "MESH":
                        cos = [o.matrix_world @ Vector(co) for co in o.bound_box]
                        zs = [p[2] for p in cos]
                    else:
                        cos = [o.location]
                        zs = [cos[0][2], cos[0][2]]

                    # Process
                    if self.raycast:
                        zs = self.bbcast(points=cos, zs=zs)

                    self.zmove_process(cos, zs)

                o.select_set(False)
                if self.ignore_selected:
                    o.hide_set(True)

        if self.ignore_selected:
            for o in self.sel_obj:
                o.hide_set(False)

        for ob in self.sel_obj:
            ob.select_set(True)

        context.view_layer.objects.active = og

        if self.editmode:
            bpy.ops.object.mode_set(mode='EDIT')
        if ignore_raycast:
            self.raycast = True

        return {"FINISHED"}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeGround)


def unregister():
    bpy.utils.unregister_class(KeGround)
