import bpy
import bmesh
from bpy.props import BoolProperty
from bpy.types import Operator
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from .._utils import vertloops, get_distance, shift_list, expand_to_island, \
    pairlink, flattened, average_vector, is_tf_applied, is_bmvert_collinear


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
    flip: BoolProperty(name="Flip Direction", default=False)
    closed: BoolProperty(default=False, options={"HIDDEN"})
    lines_only: BoolProperty(name="Edge Lines Only", default=False)
    col_lines: BoolProperty(name="Remove Collinear Verts", default=True)

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
        if self.closed or self.lines_only:
            row.enabled = False
        layout.prop(self, "invert", toggle=True)
        layout.prop(self, "flip", toggle=True)
        layout.prop(self, "lines_only", toggle=True)
        if self.lines_only:
            layout.prop(self, "col_lines")
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

        if not is_tf_applied(src_obj)[2]:
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
        active = None

        # Face Mode Macro
        if context.scene.tool_settings.mesh_select_mode[2]:
            active_face = bm.select_history.active
            if not active_face:
                self.report({"INFO"}, "Invalid Selection: No Active Element in selection")
                return {"CANCELLED"}
            og_ae = active_face.edges
            # Convert to Edge Mode
            bpy.ops.mesh.region_to_loop()
            context.tool_settings.mesh_select_mode = (False, True, False)
            bm.select_mode = {'EDGE'}
            # Set active edge
            sel_edges = [e for e in bm.edges if e.select]
            if sel_edges:
                for e in sel_edges:
                    if e in og_ae:
                        active = e
                        bm.select_history.clear()
                        bm.select_history.add(e)
                        break

        if not sel_edges:
            self.report({"INFO"}, "Invalid Selection: No edges selected")
            return {"CANCELLED"}
        else:
            sel_verts = [v for v in bm.verts if v.select]

        if not active:
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

            if self.closed:
                # simple (probably bad) winding-check
                c = pathloop[0].co
                e1 = pathloop[1].co - c
                e2 = pathloop[-2].co - c
                sd = shape_co - c
                d1 = sd.dot(e1)
                d2 = sd.dot(e2)
                if d1 < d2:
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

        if self.flip:
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
                        next_normal = Vector(edgeloop[i + 1][1].co - edgeloop[i + 1][0].co).normalized()
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
            bkp_rings = []

            for i in range(0, segcount):
                ring = ring_segments[i]
                ring.append(ring[0])
                bkp_rings.append(ring)
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
            if self.lines_only:
                gap = []
                if self.closed:
                    # Filling in the missing edge loop "gap" for lines-only mode
                    for i, j in zip(bkp_rings[0][:-1], bkp_rings[-1][:-1]):
                        gap.append([i, j])
                    es = loop_segments + gap
                else:
                    es = loop_segments
                # Nuke src shape
                if shape_faces:
                    interior_edges = set()
                    for f in shape_faces:
                        for e in f.edges:
                            interior_edges.add(e)
                        bm.faces.remove(f)
                    if interior_edges:
                        for e in interior_edges:
                            bm.edges.remove(e)
            else:
                es = new_ring_segments + loop_segments

            for e in es:
                new_edges.append(bm.edges.new(e))

            if not self.lines_only:
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

        if self.lines_only and self.col_lines:
            cvs = [v for v in bm.verts if is_bmvert_collinear(v, tolerance=3.1415)]
            bmesh.ops.dissolve_verts(bm, verts=cvs)

        # Drop all selections
        bm.select_mode = {'VERT'}
        for v in bm.verts:
            v.select = False
        bm.select_flush_mode()
        bm.select_history.clear()

        if not self.lines_only:
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
