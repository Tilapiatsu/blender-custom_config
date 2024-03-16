import bmesh
import bpy
from bpy.props import EnumProperty
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from bpy_types import Operator, Panel
from mathutils import Vector
from mathutils.geometry import intersect_point_line
from .._utils import (
    mouse_raycast,
    get_vert_nearest_mouse,
    get_distance,
    pick_closest_edge,
    get_face_islands,
    get_prefs
)


class UIDirectLoopCutModule(Panel):
    bl_idname = "UI_PT_M_DIRECTLOOPCUT"
    bl_label = "Direct Loop Cut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = ""
    bl_parent_id = "UI_PT_M_MODELING"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)
        col.operator('mesh.ke_direct_loop_cut').mode = "DEFAULT"
        col.operator('mesh.ke_direct_loop_cut', text="Direct Loop Cut & Slide").mode = "SLIDE"
        col = layout.column(align=True)
        col.operator('mesh.ke_direct_loop_cut', text="Direct Insert Vertex").mode = "VERTEX"
        col.operator('mesh.ke_direct_loop_cut', text="Direct Insert Vertex & Slide").mode = "VERTEX_SLIDE"
        row = layout.row(align=True)
        split = row.split(factor=0.35)
        split.label(text="Selection:")
        # row.label()
        split.prop(k, "dlc_so", toggle=True, text="Selected" if k.dlc_so else "Mouse-over",
                   icon="RESTRICT_SELECT_OFF" if k.dlc_so else "MOUSE_MOVE")


class KeDirectLoopCut(Operator):
    bl_idname = "mesh.ke_direct_loop_cut"
    bl_label = "Direct Loop Cut"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(items=[
        ("DEFAULT", "Default", "", 1),
        ("SLIDE", "Slide", "", 2),
        ("VERTEX", "Vertex", "", 3),
        ("VERTEX_SLIDE", "Vertex Slide", "", 4)],
        name="Mode", default="DEFAULT", options={"HIDDEN"})

    mouse_pos = [0, 0]
    screen_x = 0
    region = None
    rv3d = None
    mtx = None
    use_limit = False
    limit_polys = []
    poly_islands = []
    keep_distance = True
    nq_report = 0

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    @classmethod
    def description(cls, context, properties):
        if properties.mode == "SLIDE":
            return "DLC automatically launches GG-Slide directly after cut"
        elif properties.mode == "VERTEX":
            return "Vert-only variant of Direct Loop Cut: Inserts a vert on an edge under the mouse pointer"
        elif properties.mode == "VERTEX_SLIDE":
            return "DIV automatically launches GG-Slide directly after insertion"
        return "Inserts edge loop (or a vert with DIV) on an edge under the mouse. (No selection needed)\n" \
               "Limit cut: Select FACES to limit cut to only those faces, from edge under mouse pointer.\n" \
               "Center & Multi-cut: Select edge(s) with mouse over NOTHING/ANOTHER OBJECT"

    def get_edge_rings(self, start_edge, sv, getfac):
        max_count = 1000
        ring_edges = []
        area_bools = []
        rim_verts = []

        for loop in start_edge.link_loops:
            abools = []
            start = loop
            edges = [loop.edge]
            rim = [sv]
            prev_sv = sv

            i = 0
            while i < max_count:
                loop = loop.link_loop_radial_next.link_loop_next.link_loop_next

                if len(loop.face.edges) != 4:
                    self.nq_report += 1
                    break

                if self.use_limit:
                    abools.append(True if loop.face in self.limit_polys else False)

                if getfac:
                    for e in loop.face.edges:
                        if e != edges[-1]:
                            next_v = e.other_vert(prev_sv)
                            if next_v:
                                prev_sv = next_v
                                rim.append(next_v)
                                break

                edges.append(loop.edge)

                if loop == start or loop.edge.is_boundary:
                    break
                i += 1

            rim_verts.extend(rim)
            ring_edges.append(edges)
            area_bools.append(abools)

        rim_verts = list(set(rim_verts))
        nr = len(ring_edges)

        if nr == 2:
            # crappy workaround - better solution tbd
            if len(ring_edges[0]) == 1 and ring_edges[0][0] == start_edge:
                ring_edges = [ring_edges[1]]
                nr = 1
            elif len(ring_edges[1]) == 1 and ring_edges[1][0] == start_edge:
                ring_edges = [ring_edges[0]]
                nr = 1

        all_edges = []
        ring = []

        if nr == 1:
            # 1-directional (Border edge starts)
            all_edges = ring_edges[0]

            if self.use_limit:
                # skipping one ringe-edge (start-edge is always first) + match bools
                ring = [start_edge]
                if len(area_bools[0]) == 0:
                    ab = area_bools[1]
                else:
                    ab = area_bools[0]

                for b, e in zip(ab, ring_edges[0][1:]):
                    if b:
                        ring.append(e)
            else:
                ring = ring_edges[0]

        elif nr == 2:
            # Splicing bidirectional loops
            if self.use_limit:

                ring = [start_edge]
                for b, e in zip(area_bools[0], ring_edges[0][1:]):
                    if b and e != start_edge:
                        ring.append(e)

                rest = []
                for b, e in zip(area_bools[1], ring_edges[1][1:]):
                    if b and e not in ring:
                        rest.append(e)

                rest.reverse()
                ring = rest + ring

            elif ring_edges[0][0] == ring_edges[0][-1]:
                # Continous ring
                ring = ring_edges[0][:-1]
            else:
                # Interrupted ring
                rest = ring_edges[1][1:]
                rest.reverse()
                ring = rest + ring_edges[0]

            if ring_edges[0][0] == ring_edges[0][-1]:
                all_edges = ring_edges[0][:-1]
            else:
                rest = ring_edges[1][1:]
                rest.reverse()
                all_edges = rest + ring_edges[0]

        return ring, rim_verts, all_edges

    def get_closest_edge_point(self, vpos1, vpos2):
        mid_point_list = []
        interval = 100
        mp = region_2d_to_location_3d(self.region, self.rv3d, self.mouse_pos, vpos1)

        for i in range(1, interval):
            ival = float(i) / interval
            x = (1 - ival) * vpos1[0] + ival * vpos2[0]
            y = (1 - ival) * vpos1[1] + ival * vpos2[1]
            z = (1 - ival) * vpos1[2] + ival * vpos2[2]
            mid_point_list.append([x, y, z])

        new_mid_point = []

        for i in mid_point_list:
            a = get_distance(mp, i)
            ins = [a, i]
            new_mid_point.append(ins)

        new_mid_point.sort()

        return new_mid_point[0][-1]

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        # VP Setup
        self.region = context.region
        self.rv3d = context.region_data
        self.screen_x = int(context.region.width * .5)
        k = get_prefs()

        ob = context.object
        self.mtx = ob.matrix_world
        sel_only = k.dlc_so

        # cheap unevaluated hack - re-enable at end
        mods = []
        for m in ob.modifiers:
            if m.show_viewport:
                mods.append(m)
                m.show_viewport = False

        # Check mouse over target
        if not sel_only:
            bpy.ops.object.mode_set(mode="OBJECT")
            hit_obj, hit_wloc, hit_normal, hit_face = mouse_raycast(context, self.mouse_pos, evaluated=True)
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            hit_obj, hit_wloc, hit_normal, hit_face = None, None, None, None

        # (then) Set bmesh
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()

        if hit_face and hit_obj.name == ob.name:
            hit_face = bm.faces[hit_face]
        else:
            hit_face = None

        #
        # Selections
        #
        start_edges = []
        start_edge = []

        # start_vert = None
        get_fac = True
        og_elen = 1
        og_vec = Vector()

        # sel_verts = [v for v in bm.verts if v.select]
        sel_edges = [e for e in bm.edges if e.select]
        sel_polys = [p for p in bm.faces if p.select]
        # PH
        if sel_edges:
            start_edge = sel_edges[-1]

        if len(sel_polys) != 0:
            self.limit_polys = sel_polys
            self.use_limit = True

        if not sel_only:
            # switching to edge mode, for edge selection (pick, and result select later)
            context.tool_settings.mesh_select_mode = (False, True, False)

            if hit_face is not None:
                # Cut the one edge
                hit_2d = location_3d_to_region_2d(self.region, self.rv3d, hit_wloc)
                hit_2d = [int(hit_2d[0]), int(hit_2d[1])]
                bpy.ops.view3d.select(extend=False, location=hit_2d)
                pick = [e for e in bm.edges if e.select]

                # limit selection if in polylimit
                if sel_polys:
                    if pick:
                        if pick[0] in sel_edges:
                            sel_edges = pick
                        else:
                            sel_edges = [pick_closest_edge(context, mtx=self.mtx, mousepos=self.mouse_pos,
                                                           edges=sel_edges)]
                else:
                    sel_edges = pick

            elif hit_face is None:
                # mid-cut (all the edges)
                get_fac = False

                if sel_polys:
                    sel_edges = [pick_closest_edge(context, mtx=self.mtx, mousepos=self.mouse_pos, edges=sel_edges)]
        else:
            if sel_edges:
                sel_edges = [pick_closest_edge(context, mtx=self.mtx, mousepos=self.mouse_pos, edges=sel_edges)]

        if self.use_limit and self.mode not in {"VERTEX", "VERTEX_SLIDE"}:
            # Check for "checker" (non-continuous) poly selection
            if len(self.limit_polys) > 1:
                self.poly_islands = get_face_islands(bm=bm, sel_faces=self.limit_polys)
                if len(self.poly_islands) == 1:
                    self.poly_islands = []

        #
        # Check selection for fails
        #
        ec = len(sel_edges)
        fac = 0.5
        start_vert = None

        if ec == 0:
            self.report({"WARNING"}, "Edge selection failed/invalid - Cancelled")
            return {"CANCELLED"}

        #
        # Starting Edge Selection Handling
        #
        if ec == 1:
            start_edge = sel_edges[0]
            start_edges = [start_edge]

            floater = False
            if len(start_edge.link_faces) == 0:
                floater = True

            if get_fac and hit_face is not None or floater or sel_only:
                # Get offset factor
                start_vert = get_vert_nearest_mouse(context, Vector(self.mouse_pos), start_edge.verts, self.mtx)
                other_vert = start_edge.other_vert(start_vert)
                svco = self.mtx @ start_vert.co
                ovco = self.mtx @ other_vert.co

                if hit_wloc:
                    mouse_wpos = hit_wloc
                else:
                    mouse_wpos = self.get_closest_edge_point(svco, ovco)

                edge_point, fac = intersect_point_line(mouse_wpos, svco, ovco)

                if self.keep_distance:
                    og_elen = start_edge.calc_length()
                    og_vec = Vector((start_vert.co - other_vert.co)).normalized()

            if floater:
                # Split floater edge special
                nedge, nvert = bmesh.utils.edge_split(start_edge, start_vert, fac)
                bmesh.update_edit_mesh(me)
                bpy.ops.mesh.select_all(action="DESELECT")
                context.tool_settings.mesh_select_mode = (True, False, False)
                bm.verts.index_update()
                nvert.select_set(True)
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.ed.undo_push()

                if self.mode == "SLIDE":
                    bpy.ops.transform.vert_slide("INVOKE_DEFAULT")

                return {"FINISHED"}

        elif ec >= 2:
            start_edges = sel_edges
            get_fac = False

            if False in [bool(e.link_faces) for e in sel_edges]:
                # If even just one floater, only subdivide
                bpy.ops.mesh.subdivide()
                return {"FINISHED"}

        #
        # Cutting edge loops
        #
        new_edges = []
        new_verts = []

        if self.mode in {"VERTEX", "VERTEX_SLIDE"}:
            if start_vert is None:
                start_vert = start_edge.verts[0]
            nedge, nvert = bmesh.utils.edge_split(start_edge, start_vert, fac)
            new_verts.append(nvert)

            bmesh.update_edit_mesh(me)
            bm.verts.index_update()

        else:
            for edge in start_edges:

                # For mid-cuts, non-fac
                if start_vert is None:
                    start_vert = edge.verts[0]

                # Get ring edges (and rim) to cut
                ring, rim_verts, ring_edges = self.get_edge_rings(edge, start_vert, get_fac)

                # check for multiple start-edges on the same ring
                for r in ring_edges:
                    if r in start_edges and r != edge:
                        start_edges.remove(r)

                # making multiple ("fake") edge rings to cut if islands
                if self.poly_islands:
                    rings = []
                    for island in self.poly_islands:
                        i_ring = []
                        for p in island:
                            pedges = [e for e in p.edges if e in ring_edges]
                            i_ring.extend([e for e in pedges if e not in i_ring])
                        rings.append(i_ring)
                    if not rings:
                        # fallback justincase
                        rings = [ring]
                else:
                    rings = [ring]

                for ring in rings:
                    new_verts = []

                    for e in ring:
                        # use rim verts as start vert on edges w. fac
                        if get_fac:
                            if e.verts[0] in rim_verts:
                                sv = e.verts[0]
                            else:
                                sv = e.verts[1]
                        else:
                            # mid cuts
                            sv = e.verts[0]

                        if self.keep_distance and get_fac:
                            # This seems to work, idk, maths...
                            p1, p2 = sv.co, e.other_vert(sv).co
                            evec = Vector((p1 - p2)).normalized()
                            elen = e.calc_length()
                            e_scale = round((og_elen / elen), 3)
                            d = abs(round(og_vec.dot(evec), 3))
                            if d == 0:
                                d = 1
                            if d == 1:
                                efac = fac * (e_scale / d)
                            else:
                                efac = fac
                        else:
                            efac = fac

                        # Split ring edge
                        nedge, nvert = bmesh.utils.edge_split(e, sv, efac)
                        new_verts.append(nvert)

                    # Update
                    bmesh.update_edit_mesh(me)
                    bm.verts.index_update()

                    # Make new edge loop(s)
                    nedges = bmesh.ops.connect_verts(bm, verts=new_verts)
                    bmesh.update_edit_mesh(me)
                    bm.edges.index_update()
                    nedges = [ne for ne in nedges.values()][0]
                    new_edges.extend(nedges)

        #
        # Finish
        #
        bpy.ops.mesh.select_all(action="DESELECT")
        if self.mode in {"VERTEX", "VERTEX_SLIDE"}:
            context.tool_settings.mesh_select_mode = (True, False, False)
            for v in new_verts:
                v.select_set(True)
        else:
            for e in new_edges:
                e.select_set(True)

        me.update()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        if mods:
            for m in mods:
                m.show_viewport = True

        if self.nq_report != 0:
            print("Direct Cut: %s Non-Quads found - limited edge ring" % self.nq_report)

        if self.mode == "SLIDE":
            bpy.ops.transform.edge_slide("INVOKE_DEFAULT")
        elif self.mode == "VERTEX_SLIDE":
            bpy.ops.transform.vert_slide("INVOKE_DEFAULT")

        return {"FINISHED"}
