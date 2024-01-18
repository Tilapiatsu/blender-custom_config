import bmesh
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from .._utils import vertloops, get_distance, shift_list, is_bmvert_collinear, tri_points_vectors, expand_to_island, \
    pairlink, flattened, average_vector


class KeExtrudeAlongEdges(Operator):
    bl_idname = "mesh.ke_extrude_along_edges"
    bl_label = "Extrude Along Edges"
    bl_description = "Select (at least) 2 Edge Loops: \n" \
                     "SHAPE LOOP(s): Extruding geo loop(s). Must be continuous (closed) loop(s).\n" \
                     "PATH LOOP: The edge loop to extrude along. Must have the Active Element.\n" \
                     " Can be either continuous (closed) or not (open)."
    bl_options = {'REGISTER', 'UNDO'}

    caps: BoolProperty(name="Cap Ends", default=True)
    invert: BoolProperty(name="Flip Face Normals", default=False)
    closed: BoolProperty(default=False, options={"HIDDEN"})

    mtx = None
    coll = None
    ctx = None

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH" and context.object.mode != "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.prop(self, "caps", toggle=True)
        if self.closed:
            row.enabled = False
        layout.prop(self, "invert", toggle=True)
        layout.separator()

    def execute(self, context):
        #
        # OBJECT SELECTION
        #
        src_obj = context.object
        self.mtx = src_obj.matrix_world
        self.ctx = context

        ouc = src_obj.users_collection
        if len(ouc) > 0:
            self.coll = ouc[0]
        else:
            self.coll = context.scene.collection

        if src_obj.type != "MESH" and not src_obj.data.is_editmode:
            print("Invalid Selection: Mesh Object in Edit Mode expected")
            return {"CANCELLED"}

        if round(sum(src_obj.scale), 6) % 3 != 0:
            self.report({"INFO"}, "Note: Object Scale is not applied")

        src_obj.select_set(True)
        context.view_layer.objects.active = src_obj
        bm = bmesh.from_edit_mesh(src_obj.data)

        # Avoiding user error & confusion:
        context.scene.tool_settings.use_mesh_automerge = False
        src_obj.use_mesh_mirror_x = False
        src_obj.use_mesh_mirror_y = False
        src_obj.use_mesh_mirror_z = False

        #
        # EDGE SELECTION
        #
        sel_edges = [e for e in bm.edges if e.select]
        if not sel_edges:
            self.report({"INFO"}, "Invalid Selection: No edges selected")
            return {"CANCELLED"}
        else:
            sel_verts = [v for v in bm.verts if v.select]

        active = bm.select_history.active
        if active:
            if type(active).__name__ != "BMVert":
                active = [v for v in active.verts][0]

        if active not in sel_verts:
            self.report({"INFO"}, "Invalid Selection: No Active Element in selection")
            return {"CANCELLED"}

        #
        # SORT & ORDER SELECTION
        #
        # Note: Skipping checking winding dir for face normals - just using the bmop calc last!
        vps = [e.verts for e in sel_edges]
        islands = vertloops(vps)

        if len(islands) < 2:
            self.report({"INFO"}, "Invalid Selection: Minimum 2 edge loops expected")
            return {"CANCELLED"}

        shapeloops = []
        pathloop = []

        for island in islands:
            if active in island:
                pathloop = island
            else:
                shapeloops.append(island)

        # Check that Shapeloops are loops
        for shapeloop in shapeloops:
            if shapeloop[0] != shapeloop[-1]:
                self.report({"INFO"}, "Invalid Selection: Shape selection is not a loop")
                return {"CANCELLED"}

        shape_verts = list(set(flattened(shapeloops)))
        shape_co = average_vector([v.co for v in shape_verts])

        #
        # CLOSED OR OPEN LOOP / FIND STARTING POINT
        #
        self.closed = True if pathloop[0] == pathloop[-1] else False

        if self.closed:
            # Any vert can be starting point, 2 possible edges/directions
            idx = 0
            near = 999999

            for i, v in enumerate(pathloop):
                d = get_distance(v.co, shape_co)
                if d < near:
                    near = d
                    idx = i
            startvert = pathloop[idx]

            if pathloop[0] != startvert:
                pathloop.pop(-1)
                pathloop = shift_list(pathloop, -idx)
                pathloop.append(pathloop[0])

            # Checking which start loop edge (dir vec) is pointing the same way as the shape loop (normal)
            if self.closed:
                # candidate path vecs
                edges = [e for e in sel_edges if startvert in e.verts]
                e1p1, e1p2 = edges[0].verts[0], edges[0].verts[1]
                e2p1, e2p2 = edges[1].verts[0], edges[1].verts[1]
                ed1 = Vector(e1p2.co - e1p1.co).normalized()
                ed2 = Vector(e2p2.co - e2p1.co).normalized()

                # shape normal ref (this 3 point calc covers all cases)
                coords = [v.co for v in shape_verts if not is_bmvert_collinear(v)]
                normal, tangent = tri_points_vectors(self.mtx, Vector(), coords)

                # dot -||+ does not matter: just avoiding perp dir & using bm-op recalc normals anyways!
                if abs(normal.dot(ed1)) > abs(normal.dot(ed2)):
                    if e1p1 != pathloop[0] and e1p2 != pathloop[1]:
                        pathloop.reverse()
                else:
                    if e2p1 != pathloop[0] and e2p2 != pathloop[1]:
                        pathloop.reverse()
        else:
            # Only loop ends can be starting point, closest to shapeloop determines direction
            d1 = get_distance(pathloop[0].co, shape_co)
            d2 = get_distance(pathloop[-1].co, shape_co)
            if d2 > d1:
                startvert = pathloop[0]
            else:
                startvert = pathloop[-1]
            if pathloop[0] != startvert:
                pathloop.reverse()

        rem_shape = False
        if self.closed:
            rem_shape = True

        # Check if shape is boundary (then check connected for entire island) To:
        # A. Closed Loop: All shape faces listed for deletion
        # B. Open Loop: Making sure all the shape faces can be flipped when facing wrong way
        has_start_cap = False
        is_boundary = all(v.is_boundary for v in shape_verts)
        shape_faces = []

        if is_boundary:
            sel_island = set()
            for shape in shapeloops:
                island = expand_to_island(shape[0])
                for i in island:
                    sel_island.add(i)
            shape_faces = set()
            for v in sel_island:
                for f in v.link_faces:
                    shape_faces.add(f)
            shape_faces = list(shape_faces)

        if shape_faces:
            has_start_cap = True

        # ...and finally, link up path verts in edge-loop style pairs
        edgeloop = pairlink(pathloop)

        #
        # EXTRUDE ALONG EDGE LOOP
        #
        new_faces = []

        for shapeloop in shapeloops:
            new_verts, new_edges, loop_segments, ring_segments = [], [], [], []
            segment = shapeloop
            tot = len(edgeloop) - 1
            stot = len(shapeloop) - 1

            # Main Loop : Create new verts & edge loops
            for i, loop in enumerate(edgeloop):
                if not self.closed:
                    if i == tot:
                        # Open Loop - duplicate last edge vector
                        normal = Vector(edgeloop[i][1].co - edgeloop[i][0].co).normalized()
                        next_normal = normal + 0.001 * normal
                    else:
                        normal = Vector(loop[1].co - loop[0].co).normalized()
                        next_normal = Vector(edgeloop[i+1][1].co - edgeloop[i+1][0].co).normalized()
                else:
                    # Closed Loop - substitute last with first (& skip first segment later)
                    if i < tot:
                        normal = Vector(loop[1].co - loop[0].co).normalized()
                        next_normal = Vector(edgeloop[i + 1][1].co - edgeloop[i + 1][0].co).normalized()
                    else:
                        normal = Vector(loop[1].co - loop[0].co).normalized()
                        next_normal = Vector(edgeloop[0][1].co - edgeloop[0][0].co).normalized()

                # Create Verts via Project2Plane (TBD: simpler/more efficient maths method?)
                avg_normal = normal.lerp(next_normal, 0.5)
                plane_p = loop[1].co
                new_seg = []

                for si, v in enumerate(segment):
                    if si < stot:
                        a = v.co
                        b = a + 0.001 * normal
                        p = intersect_line_plane(a, b, plane_p, avg_normal)
                        new_vert = bm.verts.new(p)
                        new_seg.append(new_vert)
                        new_edge_loop_seg = v, new_vert
                        loop_segments.append(new_edge_loop_seg)

                if new_seg:
                    new_verts.extend(new_seg)
                    segment = new_seg
                    ring_segments.append(new_seg)

            # Prep edge rings & loop for edges & faces
            if self.closed:
                f_prev = pairlink(ring_segments[-1])
            else:
                f_prev = pairlink(shapeloop)
                f_prev.append(f_prev[0])

            face_pairs, new_ring_segments = [], []
            segcount = len(ring_segments)

            for i in range(0, segcount):
                ring = ring_segments[i]
                ring.append(ring[0])
                ringedge = pairlink(ring)
                for pair in ringedge:
                    new_ring_segments.append(pair)
                for f, pf in zip(f_prev, ringedge):
                    face_pairs.append(f + pf)
                f_prev = ringedge

            if self.closed:
                # Skipping first loop segment
                loop_segments = loop_segments[stot:]
                # Custom Last Face
                e1 = ring_segments[0][-2:]
                e2 = ring_segments[-1][-2:]
                face_pairs.append(e2 + e1)

            # Create Edges
            es = new_ring_segments + loop_segments
            for e in es:
                new_edge = bm.edges.new(e)
                new_edges.append(new_edge)

            # Create Faces
            for ep in face_pairs:
                f = ep[1], ep[3], ep[2], ep[0]
                nf = bm.faces.new(f)
                new_faces.append(nf)

            # Cap Ends
            if self.caps and not self.closed:
                cap = ring_segments[-1][:-1]
                nf = bm.faces.new(cap)
                new_faces.append(nf)
                if not has_start_cap:
                    cap = []
                    for i in shapeloop:
                        if i not in cap:
                            cap.append(i)
                    nf = bm.faces.new(cap)
                    nf.normal_flip()
                    new_faces.append(nf)

            if rem_shape:
                for v in shapeloop:
                    if v.is_valid:
                        bm.verts.remove(v)

            if not rem_shape and not self.caps:
                interior_edges = set()
                for f in shape_faces:
                    for e in f.edges:
                        interior_edges.add(e)
                    bm.faces.remove(f)
                interior_edges = [e for e in interior_edges if e not in sel_edges]
                if interior_edges:
                    for e in interior_edges:
                        bm.edges.remove(e)

        # Drop all selections
        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = False
        bm.select_flush_mode()
        bm.select_history.clear()

        # bmop to ensure face normals are facing out
        fl = shape_faces + new_faces
        fl = [f for f in fl if f.is_valid]
        bmesh.ops.recalc_face_normals(bm, faces=fl)
        if self.invert:
            for f in fl:
                f.normal_flip()
        # Finish
        bm.normal_update()
        bmesh.update_edit_mesh(src_obj.data)

        return {"FINISHED"}
