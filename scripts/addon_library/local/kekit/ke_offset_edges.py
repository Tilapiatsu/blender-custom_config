import bpy
import bmesh
from ._utils import vertloops, average_vector
from math import sin, sqrt
from mathutils import Vector
from mathutils.geometry import intersect_line_line


def angle_correct_normal(d, n, vec):
    if vec.length != 0 and n.length != 0:
        a = sin(n.angle(vec))
        if a != 0:
            return round((d / a), 4)
    return None


def ill(p1, p2, n1, n2):
    t1 = p1 + (n1 * 9001)
    t2 = p2 + (n2 * 9001)
    x = intersect_line_line(p1, t1, p2, t2)
    if x is not None:
        return x[0], t1, t2
    return x, t1, t2


class KeOffsetEdges(bpy.types.Operator):
    bl_idname = "mesh.ke_offset_edges"
    bl_label = "Extrude Edges +"
    bl_description = "Like Extrude Edges, but using Vertex or Face Normals in various modes. & with offset-only option."
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.FloatProperty(
        name="Offset Value",
        description="Distance to offset/extrude edges in Blender Unit (m)",
        soft_min=-1,
        soft_max=1,
        default=0.02,
        step=0.03,
        precision=2
    )

    op: bpy.props.EnumProperty(
        items=[("VERTEX", "Vertex Normals", "Use each vertex own normal", 1),
               ("FACE", "Face Average", "Use average normal of edge-linked faces", 2),
               ("ORTHO", "Orthogonal", "Use the orthogonal of the Face Normal. Use for border edges etc", 3),
               ("CALC_UP", "2D", "2D mode - Guess a general 'Up' from edge selection,\n"
                                 "and extrude the edge crossproduct (the 'Up' axis being flattened)\n"
                                 "(Will use face average as a fallback for a straight line selection)", 4),
               ("ACTIVE", "Active Edge", "Use Active Edge normal for all edges", 5),
               ("CURSOR", "Cursor", "Use Cursor Z-Axis direction as extrude normal for all edges", 6)
               ],
        name="Mode",
        default="FACE")

    offset_only: bpy.props.BoolProperty(
        name="Offset Only", description="Offset duplicate edges without creating faces", default=False)

    flip_normal: bpy.props.BoolProperty(
        name="Flip Normals", description="Invert the normals of new faces", default=False)

    auto_ortho: bpy.props.BoolProperty(
        name="Auto-Ortho",
        description="Automatically set Face Orthogonal mode if all selected edges are boundary edges",
        default=True)

    og_edge_sel = []
    vert_loops = []
    up = None
    cursor_vec = None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "offset")
        layout.separator(factor=0.5)
        layout.prop(self, "op", expand=True, toggle=True)
        layout.separator(factor=1)
        layout.prop(self, "offset_only", expand=True, toggle=True)
        layout.prop(self, "flip_normal", expand=True, toggle=True)
        layout.prop(self, "auto_ortho", expand=True, toggle=True)
        layout.separator(factor=1)

    def get_face_normal(self, p1, p2):
        edge, fcenter = None, None
        n = p1.normal
        # Find edge & average LF normal
        ev = (p1, p2)
        ec = [e for e in self.og_edge_sel if all(i in ev for i in e.verts)]
        if ec:
            fcenter = [f.calc_center_median() for f in ec[0].link_faces]
            n = average_vector([f.normal for f in ec[0].link_faces])
            if not n:
                # fallback to vert normal
                n = p1.normal
            return n, ec[0], fcenter[0]
        return n, edge, fcenter

    @staticmethod
    def get_ortho(fcenter, ecenter, n, edge_vec):
        n = edge_vec.cross(n).normalized()
        if fcenter:
            dir_vec = Vector((ecenter - fcenter)).normalized()
            ddir = round(dir_vec.dot(n), 4)
            if ddir < 0.0001:
                n.negate()
        n.freeze()
        return n

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "VIEW_3D" and
                context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        obj = context.object

        if sum(obj.scale) != 3:
            self.report({"INFO"}, "Caution: Scale is not applied")

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        self.og_edge_sel = [e for e in bm.edges if e.select]
        if not self.og_edge_sel:
            self.report({"INFO"}, "No edges selected?")
            return {"CANCELLED"}

        fmode = True if self.op in {"FACE", "ORTHO", "CALC_UP"} else False
        active_n = None

        # Set active as first in sequence (sorted later), for many, many reasons
        active = bm.select_history.active
        active_is_edge = isinstance(active, bmesh.types.BMEdge)
        if active_is_edge:
            for i, e in enumerate(self.og_edge_sel):
                if e == active:
                    self.og_edge_sel.insert(0, self.og_edge_sel.pop(i))
                    break
            if self.op == "ACTIVE":
                active_n = average_vector([f.normal for f in active.link_faces])

        elif not active_is_edge and self.op == "ACTIVE":
            self.report({"INFO"}, "No active edge selected?")
            return {"CANCELLED"}

        # Auto-Ortho mode if ALL edges are boundary
        if all([e.is_boundary for e in self.og_edge_sel]) and self.auto_ortho:
            # print("Auto-Ortho Mode : All edges in selection are boundary")
            self.op = "ORTHO"

        # Auto-Vertex mode if any edge has no faces linked (line/loose edge)
        for e in self.og_edge_sel:
            if not e.link_faces:
                self.op = "VERTEX"
                # print("Auto Vertex Mode : Found Loose Edge in selection (no linked faces)")
                break

        # Fall-back is face mode (later)
        if self.op == "CALC_UP":
            nvec, tvec = None, None
            evecs = [Vector(e.verts[0].co - e.verts[1].co).normalized() for e in self.og_edge_sel]
            for i, vec in enumerate(evecs):
                if i < (len(evecs) - 1):
                    d = abs(vec.dot(evecs[i + 1]))
                    if d < 0.9999:
                        nvec, tvec = vec, evecs[i + 1]
                        break
            if nvec is not None:
                self.up = nvec.cross(tvec)
                # Just to make it more likely to not need normal flipping
                if self.up.dot(Vector((0, 0, 1))) < 0.001:
                    self.up.negate()

        elif self.op == "CURSOR":
            c = context.scene.cursor
            og_cmode = str(c.rotation_mode)
            if og_cmode != "QUATERNION":
                c.rotation_mode = "QUATERNION"
            q = context.scene.cursor.rotation_quaternion
            self.cursor_vec = q @ Vector((0, 0, 1))
            c.rotation_mode = og_cmode

        # Prep for angle compensated offsets as values to vert index key dict
        offset_dict = {}
        normal_dict = {}

        # Sort verts in ordered pairs
        vloops = vertloops([e.verts for e in self.og_edge_sel])

        for vloop in vloops:
            count = len(vloop) - 1
            prev_vec = None
            prev_n = None

            # if continous loop - pre-calc "previous" edge
            if vloop[0] == vloop[-1]:
                p1 = vloop[-2]
                p2 = vloop[-1]
                prev_vec = Vector((p1.co - p2.co)).normalized()
                prev_n, edge, fcenter = self.get_face_normal(p1, p2)
                if self.op == "VERTEX":
                    prev_n = p1.normal
                elif self.op == "ORTHO":
                    ec = average_vector((p1.co, p2.co))
                    prev_n = self.get_ortho(fcenter, ec, prev_n, prev_vec)

            for i, v in enumerate(vloop):
                if i < count:
                    p1 = v
                    p2 = vloop[i + 1]
                    edge_vec = Vector((p2.co - p1.co)).normalized()
                    a_normal, b_normal = p1.normal, p2.normal
                    corner_a = None

                    if self.op == "ACTIVE":
                        a_normal, b_normal = active_n, active_n

                    elif self.op == "CURSOR":
                        a_normal, b_normal = self.cursor_vec, self.cursor_vec

                    elif fmode:
                        n, edge, fcenter = self.get_face_normal(p1, p2)
                        if self.op == "ORTHO":
                            ec = average_vector((p1.co, p2.co))
                            n = self.get_ortho(fcenter, ec, n, edge_vec)

                        if self.op == "CALC_UP" and self.up is not None:
                            cn = edge_vec.cross(self.up).normalized()
                            if cn.dot(p1.normal) < 0:
                                cn.negate()
                            # Another faceaverage fallback
                            if sum(cn) != 0:
                                n = cn

                        a_normal, b_normal = n, n

                        # line-line check for corner verts
                        if prev_vec is not None and prev_n is not None:
                            # unless it's just the same vec
                            d = round(prev_vec.dot(edge_vec), 4)
                            if abs(d) < 0.9:
                                new_p1 = p1.co + (a_normal * self.offset)
                                prev_p1 = p1.co + (prev_n * self.offset)
                                corner_a, new_vec, npvec = ill(new_p1, prev_p1, edge_vec, prev_vec)
                                if corner_a:
                                    a_normal = Vector((corner_a - p1.co)).normalized()
                                    if self.offset < 0:
                                        a_normal.negate()

                    prev_vec = edge_vec
                    prev_n = b_normal

                    if self.op == "ACTIVE" or self.op == "CURSOR":
                        a_offset, b_offset = self.offset, self.offset
                    else:
                        a_offset = angle_correct_normal(self.offset, a_normal, edge_vec)
                        b_offset = angle_correct_normal(self.offset, b_normal, edge_vec)

                    if a_offset is None:
                        a_offset = 0
                    if b_offset is None:
                        b_offset = 0

                    if p1.index not in offset_dict or corner_a is not None:
                        offset_dict[p1.index] = a_offset
                        normal_dict[p1.index] = a_normal
                    if p2.index not in offset_dict:
                        offset_dict[p2.index] = b_offset
                        normal_dict[p2.index] = b_normal

        new_verts = []
        new_edges = []
        new_faces = []
        new_vert_pairs = []

        # Create the new verts, and sort for geo creation pass 2
        for loop in vloops:
            vps = []
            for v in loop:
                offset = offset_dict[v.index]
                n = normal_dict[v.index]
                new_co = v.co + (n * offset)
                new = bm.verts.new(new_co)
                vps.append((v, new))
                new_verts.append(new)
            new_vert_pairs.append(vps)

        # Geo creation pass2 (Edges and Faces)
        for pairs in new_vert_pairs:
            count = len(pairs)
            for i, pair in enumerate(pairs):
                if i < count - 1:
                    op = pairs[i + 1]
                    if self.offset_only:
                        edge = bm.edges.new((pair[1], op[1]))
                    else:
                        p = pair[0], pair[1], op[1], op[0]
                        f = bm.faces.new(p)
                        new_faces.append(f)
                        edge = [e for e in pair[1].link_edges if e.other_vert(pair[1]) == op[1]][0]
                    new_edges.append(edge)

        for e in self.og_edge_sel:
            e.select_set(False)

        for edge in new_edges:
            edge.select_set(True)

        bm.normal_update()
        for f in new_faces:
            f.normal_flip()
            if self.flip_normal:
                f.normal_flip()

        # Create UVs
        # Nicely lines up uvs (in rough approx size) just under 0-1 space for easy access
        if not self.offset_only:
            uv_layer = bm.loops.layers.uv.verify()
            s = sqrt(new_faces[0].calc_area())
            uvs = [(0.0, -s), (0.0, -s * 2), (s, -s * 2), (s, -s)]
            offset = 0
            for face in new_faces:
                for i, loop in enumerate(face.loops):
                    loop_uv = loop[uv_layer]
                    loop_uv.uv[0] = uvs[i][0] + offset
                    loop_uv.uv[1] = uvs[i][1]
                offset += s

        bm.select_history.clear()
        bm.select_history.add(new_edges[0])

        # lazy continous loop cleanup:
        bmesh.ops.remove_doubles(bm, verts=new_verts, dist=0.00001)

        # bm.normal_update()
        bmesh.update_edit_mesh(mesh)
        mesh.update()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(KeOffsetEdges)


def unregister():
    bpy.utils.unregister_class(KeOffsetEdges)
