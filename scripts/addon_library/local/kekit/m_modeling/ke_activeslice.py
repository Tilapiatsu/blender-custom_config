from math import radians

import bmesh
import bpy
from bpy.props import EnumProperty, BoolProperty, BoolVectorProperty
from bpy.types import Operator
from mathutils import Matrix, Vector


def rotate_vector(vec, axis):
    return Matrix.Rotation(radians(90.0), 4, axis) @ vec


def calc_plane(mtx, p1, p2):
    np1 = mtx.inverted() @ p1
    np2 = mtx.inverted() @ p2
    n = Vector((np2 - np1)).normalized()
    return np1, n


class KeActiveSlice(Operator):
    bl_idname = "mesh.ke_activeslice"
    bl_label = "Active Slice"
    bl_description = "Slice selected elements by MODE:\n" \
                     "VERTEX: Global Orientation using Active Vert + View for nearest Global Axis\n" \
                     "EDGE: Active Edge direction + calculated linked face orientation\n" \
                     "FACE: Active Face as cutting plane"
    bl_options = {'REGISTER', 'UNDO'}

    axis : EnumProperty(items=[
        ("H", "Horizontal", "", "", 1),
        ("V", "Vertical", "", "", 2)],
        name="Cut Direction",
        default="H"
    )
    edge_face_switch : BoolProperty(
        name="Plane Toggle",
        description="Toggles between the active edge's linked faces (if > 1) used for plane calculation\n"
                    "Note: Only useful if the linked faces have different orientation",
        default=False
    )
    select_result : BoolProperty(
        name="Select Result",
        default=True
    )
    sel_mode: BoolVectorProperty(
        default=(False, False, False),
        options={"HIDDEN"}
    )

    target_geo = []
    plane_p = [0, 0, 0]
    plane_n = [0, 0, 1]
    active_idx = None
    mtx = Matrix()
    sel = []
    p1 = None
    p2 = None

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        if self.sel_mode[0]:
            layout.prop(self, "axis", expand=True)
        elif self.sel_mode[1]:
            layout.prop(self, "edge_face_switch", toggle=True)
        layout.separator()
        layout.prop(self, "select_result", toggle=True)
        layout.separator()

    def sort_geo(self, bm, selmode, ao):
        # SKIPS ENTIRE MESH IF ONLY AE SELECTED
        if ao:
            t = [i for i in self.sel if i.index != self.active_idx]
        else:
            t = [i for i in self.sel]
        if not t:
            self.target_geo = []
            return
        # GET TARGET GEO
        if selmode[2]:
            target_f = t
            target_e = [e for e in bm.edges if e.select]
            target_v = [v for v in bm.verts if v.select]
        elif selmode[1]:
            target_f = [f for f in bm.faces if f.select]
            target_e = t
            target_v = [v for v in bm.verts if v.select]
        else:
            target_f = [f for f in bm.faces if f.select]
            target_e = [e for e in bm.edges if e.select]
            target_v = t
        # BMOP DEMANDS THIS LAYOUT:
        self.target_geo = target_v + target_e + target_f

    def execute(self, context):
        # CUTTER OBJECT
        sel_mode = context.tool_settings.mesh_select_mode[:]
        self.sel_mode = sel_mode

        active_obj = context.active_object
        if not active_obj:
            active_obj = context.object
        if not active_obj:
            print("Invalid Selection")
            return {"CANCELLED"}

        self.mtx = active_obj.matrix_world
        bm = bmesh.from_edit_mesh(active_obj.data)
        active = bm.select_history.active
        sel_check = False

        # CHECK SELECTIONS & GET ACTIVE ELEMENT DATA
        if active:
            if sel_mode[2]:
                self.sel = [f for f in bm.faces if f.select]

                if active in self.sel:
                    sel_check = True
                    # (PLANE) NORMAL-BY-VERT-CO'S (BEACUSE REASONS?)
                    self.p1 = active.verts[0].co
                    self.p2 = self.p1 + (active.normal * 0.5)
                    self.p1 = self.mtx @ self.p1
                    self.p2 = self.mtx @ self.p2

            elif sel_mode[1]:
                self.sel = [e for e in bm.edges if e.select]

                if active in self.sel:
                    sel_check = True
                    # EVAL LINK-FACES FOR PERP.PLANE N
                    p1 = active.verts[0].co
                    p2 = active.verts[1].co
                    v1 = Vector((p2 - p1)).normalized()

                    lf = active.link_faces
                    if not lf:
                        plane_n = v1.orthogonal().cross(v1).normalized()
                    else:
                        if len(lf) == 2:
                            # CANDIDATES FOR PLANE N
                            c1 = lf[0].normal.cross(v1).normalized()
                            c2 = lf[1].normal.cross(v1).normalized()
                            if c1.dot(v1) < c2.dot(v1):
                                plane_n = c1
                                if self.edge_face_switch:
                                    plane_n = c2
                            else:
                                plane_n = c2
                                if self.edge_face_switch:
                                    plane_n = c1
                        else:
                            plane_n = lf[0].normal.cross(v1).normalized()

                    self.p1 = p1
                    self.p2 = self.p1 + (plane_n * 0.5)
                    self.p1 = self.mtx @ self.p1
                    self.p2 = self.mtx @ self.p2

            else:
                self.sel = [v for v in bm.verts if v.select]

                if active in self.sel:
                    sel_check = True
                    self.plane_p = active.co

                    # GET AXIS FROM NEAREST VIEWPLANE AXIS (PERP.)
                    rm = context.space_data.region_3d.view_matrix
                    v = Vector(rm[2])
                    x, y, z = abs(v.x), abs(v.y), abs(v.z)

                    if x > y and x > z:
                        vec = Vector((0, 0, 1))
                        if self.axis == "V":
                            vec = rotate_vector(vec, "X")
                    elif y > x and y > z:
                        vec = Vector((0, 0, 1))
                        if self.axis == "V":
                            vec = rotate_vector(vec, "Y")
                    else:
                        # Z AXIS VIEW: CHECK WHICH AXIS IS HORIZONTAL (RELATIVELY)
                        h = Vector(rm[0])
                        h_x, h_y = abs(h.x), abs(h.y)

                        if h_x > h_y:
                            vec = Vector((0, 1, 0))
                        else:
                            vec = Vector((1, 0, 0))

                        if self.axis == "V":
                            vec = rotate_vector(vec, "Z")

                    self.plane_n = vec

        if not sel_check:
            self.report({"INFO"}, "Invalid selection")
            return {"CANCELLED"}

        self.active_idx = active.index

        # PROCESS SELECTED EDIT MESHES
        sel_objects = [o for o in context.selected_objects if o.type == "MESH"]
        tot = 0

        for obj in sel_objects:
            m = obj.matrix_world
            bm = bmesh.from_edit_mesh(obj.data)
            ex_ae = []

            # CALCULATE CUTTING PLANE
            if sel_mode[2]:
                bm.faces.ensure_lookup_table()
                if obj == active_obj:
                    ex_ae = bm.faces[self.active_idx].edges[:]

                self.sel = [f for f in bm.faces if f.select]
                plane_p, plane_n = calc_plane(m, self.p1, self.p2)

            elif sel_mode[1]:
                bm.edges.ensure_lookup_table()
                if obj == active_obj:
                    ex_ae = [bm.edges[self.active_idx]]

                self.sel = [e for e in bm.edges if e.select]
                plane_p, plane_n = calc_plane(m, self.p1, self.p2)

            else:
                bm.verts.ensure_lookup_table()
                self.sel = [v for v in bm.verts if v.select]
                upa = m @ self.plane_p
                upb = upa + self.plane_n
                plane_p, plane_n = calc_plane(m, upa, upb)
                # CUSTOM P OVERRIDE
                p = self.mtx @ self.plane_p
                p = m.inverted() @ p
                plane_p = p

            # PROCESS TARGET SELECTION
            self.target_geo = []  # RESET JIC

            if obj == active_obj:
                self.sort_geo(bm, sel_mode, ao=True)
            else:
                self.sort_geo(bm, sel_mode, ao=False)

            new_edges = []

            if self.target_geo:
                # SLICE!
                geom = bmesh.ops.bisect_plane(
                    bm,
                    geom=self.target_geo,
                    dist=0.000001,
                    plane_co=plane_p,
                    plane_no=plane_n
                )
                new_edges = [i for i in geom['geom_cut'] if isinstance(i, bmesh.types.BMEdge)]
                if obj == active_obj:
                    # ACTIVES EDGES ARE COUNTED AS NEW EDGES -> FILTER W. EXCLUDE LIST
                    new_edges = [e for e in new_edges if e not in ex_ae]
                tot += len(new_edges)

            # CLEANUP SELECTION & UPDATE
            for v in bm.verts:
                v.select = False
            for e in bm.edges:
                e.select = False
            for f in bm.faces:
                f.select = False

            if self.select_result and new_edges:
                for e in new_edges:
                    e.select = True

            bmesh.update_edit_mesh(obj.data)

        if tot >= 1 and self.select_result:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        elif tot == 0:
            self.report({"INFO"}, "Invalid Selection / View Angle / Plane Not Intersecting")

        return {"FINISHED"}
