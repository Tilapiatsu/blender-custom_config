import bmesh
import numpy as np
import bpy
from bpy.props import EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator
from mathutils import Vector
from .._utils import average_vector, point_axis_raycast, get_vertex_islands


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


def co_zs(o, sel_verts):
    cos = [o.matrix_world @ v.co for v in sel_verts]
    zs = [p[2] for p in cos]
    zs.sort()
    return cos, zs


def bb_world_coords(obj):
    n = len(obj.data.vertices)
    coords = np.empty((n * 3), dtype=float)
    obj.data.vertices.foreach_get("co", coords)
    coords = np.reshape(coords, (n, 3))
    coords4d = np.empty(shape=(n, 4), dtype=float)
    coords4d[::-1] = 1
    coords4d[:, :-1] = coords
    npwc = np.einsum('ij,aj->ai', obj.matrix_world, coords4d)[:, :-1]
    bb_x = np.sort(npwc[:, 0])
    bb_y = np.sort(npwc[:, 1])
    bb_z = np.sort(npwc[:, 2])
    # BB: Bottom corners first, then top
    bb = [
        Vector((bb_x[0], bb_y[0], bb_z[0])),
        Vector((bb_x[-1], bb_y[0], bb_z[0])),
        Vector((bb_x[-1], bb_y[-1], bb_z[0])),
        Vector((bb_x[0], bb_y[-1], bb_z[0])),
        Vector((bb_x[0], bb_y[0], bb_z[-1])),
        Vector((bb_x[-1], bb_y[0], bb_z[-1])),
        Vector((bb_x[-1], bb_y[-1], bb_z[-1])),
        Vector((bb_x[0], bb_y[-1], bb_z[-1]))
    ]
    return npwc, bb


class KeGround(Operator):
    bl_idname = "view3d.ke_ground"
    bl_label = "Ground (or Center)"
    bl_description = "Ground (or Center) selected object(s) - or selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    op: EnumProperty(
        items=[("GROUND", "Ground", "Drops selection so that the bottom is on Z0 (or raycast point)", 1),
               ("CENTER", "Ground Midpoint", "Drops selection so that its midpoint is Z0 (or raycast point)", 2),
               ("CENTER_GROUND", "Ground & Center XY", "Drops Z to ground and zeros X & Y", 3),
               ("CENTER_ALL", "Center XYZ", "Drops Z to midpoint, and zeros X & Y", 4),
               ("UNDER", "Under-Ground", "Drops selection -below- ground (Z0 or raycast point)", 5)],
        name="Operation", default="GROUND")

    group: EnumProperty(
        items=[
            ("NONE", "Individual", "Process each selected object/vertex separately", 1),
            ("AVG", "Group Averaged", "Average center of selection as group center. ", 2),
            ("CTX", "Group Active", "Active object/element in selection as group center", 3),
            ("ISLE", "Loose Parts",
             "Edit Mode: (Edge-connected) Selection 'mesh islands' / loose parts\n"
             "E.g.: Edge-rings on a pipe/cylinder, or face-selection\n"
             "Object Mode: Each object(s) 'loose parts' grounded separately", 4)],
        name="Process", default="CTX")

    custom_z: FloatProperty(name="Ground =", default=0,
                            description="Override for custom position on the Global Z axis (default Z=0).")

    raycast: BoolProperty(name="Raycast", default=True,
                          description="Stops on obstructions on the way down (or Ground if nothing is hit)")

    ignore_selected: BoolProperty(name="Ignore Sel.Obj", default=False,
                                  description="Ignore selected Object(s) when raycasting")

    sel_obj = []
    editmode = False
    ctx = None
    ctx_obj_active_em = None
    ignored_faces = []
    current_obj = None

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "group", expand=True)
        layout.prop(self, "custom_z")
        layout.separator(factor=0.5)
        col = layout.column(align=True)
        # Only Ground op is valid in per-vertex context:
        if self.group in {"NONE"} and context.mode != "OBJECT" or \
                self.group == "ISLE" and context.mode == "OBJECT":
            col.enabled = False
        col.prop(self, "op", expand=True)
        layout.separator(factor=0.5)
        row = layout.row()
        if self.op == "CENTER_ALL":
            row.enabled = False
        row.prop(self, "raycast")
        row = layout.row()
        # if context.mode != "OBJECT":
        #     row.enabled = False
        row.prop(self, "ignore_selected")
        layout.separator(factor=1)

    def bbcast(self, points, zs):
        hits = []
        # low_z needs set var here?!:
        low_z = zs[0]
        for p in points:
            result, hit = self.ground_raycast(low_z=low_z, point=p, zs=zs)
            if hit is not None:
                hits.append([result[0], result[-1]])
        if hits:
            return sorted(hits, key=lambda z: z[0])[0]
        return zs

    def ground_raycast(self, low_z, point, zs):
        point[2] -= 0.0009  # hack so it doesn't trace itself...
        best_obj, hit_wloc, hit_normal, hit_face = point_axis_raycast(self.ctx, vec_point=point, axis=2)
        ign = self.ignored_faces
        if best_obj != self.current_obj and hit_face in self.ignored_faces:
            ign = []
        if hit_wloc is not None and hit_face not in ign:
            hit = hit_wloc
            dist = low_z - hit[2]
            zs[-1] = dist + (zs[-1] - zs[0])
            zs[0] = dist
        else:
            hit = None
        return zs, hit

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

    def mode_co_process(self, co, z, aco, zs):
        new_co = co
        if self.op == "GROUND":
            nz = round(co[2] - z, 6) - self.custom_z * -1
            new_co = Vector((co[0], co[1], nz))

        elif self.op == "CENTER":
            offset = z + ((zs[-1] - zs[0]) / 2)
            nz = round(co[2] - offset, 6) - self.custom_z * -1
            new_co = Vector((co[0], co[1], nz))

        elif self.op == "CENTER_GROUND":
            nx = co[0] - aco[0]
            ny = co[1] - aco[1]
            nz = round(co[2] - z, 6) - self.custom_z * -1
            new_co = Vector((nx, ny, nz))

        elif self.op == "CENTER_ALL":
            nx = co[0] - aco[0]
            ny = co[1] - aco[1]
            offset = z + (aco[2] - zs[0])
            nz = co[2] - round(offset, 6) - self.custom_z * -1
            new_co = Vector((nx, ny, nz))

        elif self.op == "UNDER":
            offset = z + (zs[-1] - zs[0])
            nz = co[2] - round(offset, 6) - self.custom_z * -1
            new_co = Vector((co[0], co[1], nz))
        return new_co

    def island_zmove(self, o, islands):
        for island in islands:
            coords, zs = co_zs(o, island)
            if self.raycast:
                z = self.bbcast(points=coords, zs=zs)[0]
            else:
                z = zs[0]
            for v in island:
                co = o.matrix_world @ v.co
                new_co = self.mode_co_process(co, z, co, zs)
                v.co = o.matrix_world.inverted() @ new_co

    def execute(self, context):
        # Prep/Selection Check
        self.ignored_faces = []
        self.sel_obj = [o for o in context.selected_objects]
        if not self.sel_obj:
            self.report({"INFO"}, "Ground: Selection Error?")
            return {'CANCELLED'}

        if context.object.type == "MESH":
            self.editmode = bool(context.object.data.is_editmode)
        else:
            self.editmode = False

        self.ctx = context
        og = context.object if context.object in self.sel_obj else self.sel_obj[0]
        active = True if context.active_object in self.sel_obj else False
        if not active:
            context.view_layer.objects.active = og

        # Need to grab and use active vert coords from context obj (only) here
        if self.editmode and self.group == "CTX":
            bm = bmesh.from_edit_mesh(og.data)
            active = bm.select_history.active
            if active:
                if type(active).__name__ == "BMVert":
                    self.ctx_obj_active_em = og.matrix_world @ active.co
                else:
                    c = [og.matrix_world @ v.co for v in active.verts]
                    self.ctx_obj_active_em = sorted(c, key=lambda vz: vz[2])[0]

        bpy.ops.object.mode_set(mode='OBJECT')

        if not self.editmode and self.group == "ISLE":
            # Sorting mesh islands by z pos for stacking: TBD (probably not)
            self.ignore_selected = True

        if self.ignore_selected:
            for o in self.sel_obj:
                o.hide_set(True)

        # OBJECT MNODE + GROUP
        if not self.editmode and self.group not in {"NONE", "ISLE"}:
            grp_cos = []
            grp_zs = []

            if self.group == "AVG":
                # print("GROUP w. averaged values")
                for o in self.sel_obj:
                    o.hide_set(True)
                    if og.type == "MESH":
                        grp_cos.extend(bb_world_coords(o)[1])
                    else:
                        grp_cos = [o.location] * 8
                grp_avg = average_vector(grp_cos)
                grp_cos = [grp_avg]
                grp_zs = [p[2] for p in grp_cos]
                grp_zs.sort()
                if self.raycast:
                    grp_zs, hit = self.ground_raycast(low_z=grp_cos[0][2], point=grp_cos[0], zs=grp_zs)

            elif self.group == "CTX":
                # print("GROUP w. active(context.object) values")
                og.hide_set(True)
                if og.type == "MESH":
                    grp_cos = bb_world_coords(og)[1]
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
            # print("INDIVIDUALLY Process each Object -or- Edit Mode Element selected")
            if self.group == "ISLE" and self.op in {"CENTER_GROUND", "CENTER_ALL"}:
                # print("G&C: Useless operation for Isle Mode - reverted to Ground")
                self.op = "GROUND"

            bpy.ops.object.select_all(action="DESELECT")

            for o in self.sel_obj:
                self.current_obj = o
                o.select_set(True)
                context.view_layer.objects.active = o
                if self.ignore_selected:
                    o.hide_set(True)

                sel_verts = [v for v in o.data.vertices if v.select] if self.editmode else []
                if self.group != "NONE":
                    self.ignored_faces = [f.index for f in o.data.polygons if f.select] if self.editmode else []

                if sel_verts:
                    # self.ignore_selected = True
                    sel_edges = [e for e in o.data.edges if e.select]

                    if self.group == "ISLE" and not sel_edges:
                        # print("Ground or Center: No connected geo found in selection - Using Group Average")
                        self.group = "AVG"

                    if self.group == "NONE":
                        # print("NONE: Only Ground op is valid in per-vertex context")
                        self.op = "GROUND"
                        # Get z-distance
                        coords, zs = co_zs(o, sel_verts)
                        if self.raycast:
                            projz = []
                            for co in coords:
                                z = self.ground_raycast(low_z=co[2], point=co, zs=[co[2]])[0][0]
                                projz.append(z)
                            zs = projz
                        else:
                            zs = [c[2] for c in coords]
                        # Move verts
                        for v, z in zip(sel_verts, zs):
                            co = o.matrix_world @ v.co
                            co[2] -= round(z, 6)
                            v.co = o.matrix_world.inverted() @ co

                    elif self.group == "AVG":
                        coords, zs = co_zs(o, sel_verts)
                        aco = average_vector(coords)
                        avg_offset = aco[2] - zs[0]
                        aco[2] = zs[0]

                        if self.raycast:
                            z = self.ground_raycast(low_z=zs[0], point=aco, zs=[zs[0], zs[-1]])[0][0]
                        else:
                            z = zs[0]

                        z += avg_offset

                        for v in sel_verts:
                            co = o.matrix_world @ v.co
                            new_co = self.mode_co_process(co, z, aco, zs)
                            v.co = o.matrix_world.inverted() @ new_co

                    elif self.group == "CTX":
                        coords, zs = co_zs(o, sel_verts)
                        # Get active vert coord as grp center. Fallback: random (index 0)
                        if self.ctx_obj_active_em is not None:
                            aco = self.ctx_obj_active_em
                        else:
                            aco = coords[0]
                            aco[2] = zs[0]

                        if self.raycast:
                            z = self.ground_raycast(low_z=aco[2], point=aco, zs=[zs[0], zs[-1]])[0][0]
                        else:
                            z = zs[0]

                        for v in sel_verts:
                            co = o.matrix_world @ v.co
                            new_co = self.mode_co_process(co, z, aco, zs)
                            v.co = o.matrix_world.inverted() @ new_co

                    elif self.group == "ISLE":
                        # print("ISLE MODE")
                        islands = get_vertex_islands(sel_verts, sel_edges, is_bm=False)
                        self.island_zmove(o, islands)

                    o.data.update()

                else:
                    # print("OBJECT MODE -> Edit Mode Parts Process")
                    if self.group == "ISLE":
                        # print("ISLE MODE - PER OBJ")
                        islands = get_vertex_islands(o.data.vertices, o.data.edges, is_bm=False)
                        self.island_zmove(o, islands)
                        o.data.update()
                    else:
                        # OBJECT MODE - Individual
                        if og.type == "MESH":
                            npcoords, coords = bb_world_coords(o)
                            zs = [p[2] for p in coords]
                        else:
                            coords = [og.location] * 8
                            zs = [p[2] for p in coords]
                            zs.sort()

                        # Process
                        if self.raycast:
                            o.hide_set(True)
                            zs = self.bbcast(points=coords, zs=zs)

                        o.hide_set(False)
                        o.select_set(True)
                        self.zmove_process(coords, zs)

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

        return {"FINISHED"}
