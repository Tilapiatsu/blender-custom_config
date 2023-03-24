import bpy
import bmesh
from bpy.types import Operator
from ._utils import get_duplicates, pick_closest_edge


def get_edge_rings(start_edge, sel):
    max_count = 1000
    ring_edges = []
    area_bools = []
    faces_visited = []

    for loop in start_edge.link_loops:
        abools = []
        start = loop
        edges = [loop.edge]

        i = 0
        while i < max_count:
            loop = loop.link_loop_radial_next.link_loop_next.link_loop_next

            if len(loop.face.edges) != 4:
                # self.nq_report += 1
                break

            if loop.face in sel:
                abools.append(True)
                faces_visited.extend([loop.face])
            else:
                abools.append(False)
                break

            edges.append(loop.edge)

            if loop == start or loop.edge.is_boundary:
                break
            i += 1

        ring_edges.append(edges)
        area_bools.append(abools)

    nr = len(ring_edges)

    if nr == 2:
        # crappy workaround - better solution tbd
        if len(ring_edges[0]) == 1 and ring_edges[0][0] == start_edge:
            ring_edges = [ring_edges[1]]
            nr = 1
        elif len(ring_edges[1]) == 1 and ring_edges[1][0] == start_edge:
            ring_edges = [ring_edges[0]]
            nr = 1

    ring = []

    if nr == 1:
        # 1-directional (Border edge starts)
        ring = [start_edge]
        if len(area_bools[0]) == 0:
            ab = area_bools[1]
        else:
            ab = area_bools[0]

        for b, e in zip(ab, ring_edges[0][1:]):
            if b:
                ring.append(e)

    elif nr == 2:
        # Splicing bi-directional loops
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

    return ring, list(set(faces_visited))


class KeContextConnect(Operator):
    bl_idname = "mesh.ke_context_connect"
    bl_label = "Context Connect"
    bl_description = "VERTS: Connect Verts\n" \
                     "EDGES: Subdivide\n" \
                     "FACES: Splits along selection (Single face uses mouse pos)\n" \
                     "NO SELECTION: Knife Tool"
    bl_options = {'REGISTER', 'UNDO'}

    nr: bpy.props.IntProperty(name="Edge Cuts", min=1, max=99, default=1)
    square: bpy.props.BoolProperty(name="Square Corners", default=True)

    show_cuts = False
    face_mode = False
    region = None
    rv3d = None
    screen_x = 0
    mtx = None
    mouse_pos = [0, 0]
    visited = []

    def draw(self, context):
        layout = self.layout
        if self.show_cuts:
            layout.use_property_split = True
            layout.prop(self, "nr")
            if self.face_mode:
                layout.prop(self, "square", expand=True, toggle=True)

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def invoke(self, context, event):
        self.mouse_pos[0] = event.mouse_region_x
        self.mouse_pos[1] = event.mouse_region_y
        return self.execute(context)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]
        single_edge = False

        if sel_mode[2]:
            self.face_mode = True

        # No selection (or 1 vert) -> knife
        context.object.update_from_editmode()
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        if not sel_obj:
            sel_obj.append(context.object)

        vsel = []
        for o in sel_obj:
            vsel.extend([v for v in o.data.vertices if v.select])
        if not vsel or len(vsel) == 1:
            bpy.ops.mesh.knife_tool('INVOKE_DEFAULT')
            return {'FINISHED'}

        elif sel_mode[0]:
            if len(vsel) == 2:
                sub = False
                edges = [e for e in context.object.data.edges if e.select]
                if edges:
                    everts = edges[0].vertices[:]
                    selverts = [v.index for v in vsel]
                    if all([i for i in everts if i in selverts]):
                        sub = True
                if sub:
                    bpy.ops.mesh.subdivide('INVOKE_DEFAULT')
                    return {'FINISHED'}
            try:
                bpy.ops.mesh.vert_connect_path('INVOKE_DEFAULT')
            except Exception as e:
                print("keCC - Using Vert Connect instead of Vert Connect Path:\n", e)
                bpy.ops.mesh.vert_connect('INVOKE_DEFAULT')

        elif sel_mode[1]:
            tot = []
            report = []

            for obj in sel_obj:
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                bm.edges.ensure_lookup_table()

                sel = [e for e in bm.edges if e.select]
                if sel:
                    tot.append(len(sel))
                    for e in sel:
                        e.select = False

                    new_edges = bmesh.ops.subdivide_edges(bm, edges=sel, cuts=self.nr, use_grid_fill=False)
                    for e in new_edges['geom_inner']:
                        e.select = True

                    bmesh.update_edit_mesh(me)
                else:
                    report.append(obj.name)

            if any(t == 1 for t in tot):
                # print("Single Edge selected - Switching to Vert Mode")
                # To make it easier to see added verts...
                single_edge = True
                bpy.ops.mesh.select_mode(type='VERT')
                sel_mode = (True, False, False)

            if report:
                r = ", ".join(report)
                self.report({"INFO"}, 'No edges selected on "%s"' % r)

        elif sel_mode[2]:

            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    self.region = area.regions[-1]
                    self.rv3d = area.spaces.active.region_3d

            self.screen_x = int(self.region.width * .5)

            if not sel_obj:
                self.report({"INFO"}, "No objects selected!")
                return {'CANCELLED'}

            for obj in sel_obj:
                self.mtx = obj.matrix_world.copy()
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                bm.edges.ensure_lookup_table()

                sel_poly = [p for p in bm.faces if p.select]
                # sel_verts = [v.index for v in bm.verts if v.select]

                if len(sel_poly) == 1:
                    start_edge = pick_closest_edge(context, mtx=self.mtx, mousepos=self.mouse_pos,
                                                   edges=sel_poly[0].edges)
                    end_edge = None
                    for e in sel_poly[0].edges:
                        if not any(v in e.verts for v in start_edge.verts):
                            end_edge = e
                            break

                    if end_edge is None:
                        print("ContextConnect: No suitable 2nd edge found on the face")
                        return {"CANCELLED"}

                    ring = [start_edge, end_edge]

                    for e in bm.edges:
                        e.select = False

                    new_edges = bmesh.ops.subdivide_edges(bm, edges=ring, cuts=self.nr, use_grid_fill=False)
                    for e in new_edges['geom_inner']:
                        e.select = True

                elif len(sel_poly) > 1:
                    p_edges = []
                    for p in sel_poly:
                        p_edges.extend(p.edges)

                    shared_edges = get_duplicates(p_edges)
                    sed_bkp = shared_edges.copy()

                    if not shared_edges:
                        self.report({"INFO"}, "Invalid (Discontinuous?) selection")
                        return {"CANCELLED"}

                    rings = []
                    ring, self.visited = get_edge_rings(shared_edges[0], sel_poly)
                    rings.append(ring)

                    if (len(ring) - 2) != len(shared_edges):

                        sel1 = [v.index for v in bm.verts if v.select]

                        sanity = 9001
                        shared_edges = [e for e in shared_edges if e not in ring]

                        while shared_edges or sanity > 0:
                            if shared_edges:
                                ring, fvis = get_edge_rings(shared_edges[0], sel_poly)
                                self.visited.extend(fvis)
                                rings.append(ring)
                                shared_edges = [e for e in shared_edges if e not in ring]
                            else:
                                break
                            sanity -= 1

                        # improvised solution here...as we go ;D
                        occurances = [[x, self.visited.count(x)] for x in set(self.visited)]
                        corners = []
                        cedges = []
                        for item in occurances:
                            if item[1] > 1:
                                corners.append(item[0])
                                cedges.extend(item[0].edges)

                        new_rings = []

                        for r in rings:
                            discard = []
                            for e in r:
                                if e not in sed_bkp and e in cedges:
                                    discard.append(e)

                            c = [e for e in r if e not in discard]
                            new_rings.append(c)

                        rings = new_rings

                        # QUAD CORNERS
                        if self.square:

                            redges = [e for r in rings for e in r]
                            nc = []

                            for p in corners:
                                if len(p.verts) == 4:

                                    pedges = [e for e in p.edges if e in redges]

                                    if len(pedges) == 2:
                                        ev = pedges[0].verts[:] + pedges[1].verts[:]
                                        inner_vert = get_duplicates(ev)
                                        outer_vert = [v for v in p.verts if v not in ev]

                                        if inner_vert and outer_vert:
                                            cv_verts = [inner_vert[0], outer_vert[0]]
                                            nc.append(cv_verts)
                            if nc:
                                for vp in nc:
                                    ret = bmesh.ops.connect_verts(bm, verts=vp)
                                    new_cedges = ret["edges"]
                                    bmesh.update_edit_mesh(me)

                                    if new_cedges:
                                        rings[0].extend(new_cedges)

                        # PREP for cuts
                        for e in bm.edges:
                            e.select_set(False)

                        for r in rings:
                            for e in r:
                                e.select_set(True)

                        # I should find a cleaner bmesh solution for cornering, but meh...
                        bpy.ops.mesh.subdivide(number_cuts=self.nr)
                        bpy.ops.mesh.tris_convert_to_quads()

                        bm.verts.ensure_lookup_table()
                        sel2 = [v for v in bm.verts if v.select]

                        bpy.ops.mesh.select_all(action="DESELECT")

                        for v in sel2:
                            if v.index not in sel1:
                                v.select_set(True)

                        bpy.ops.mesh.select_mode(type='VERT')

                    else:
                        # Sinple one-ring direction cut
                        if rings:

                            for e in bm.edges:
                                e.select = False

                            for ring in rings:
                                new_edges = bmesh.ops.subdivide_edges(bm, edges=ring, cuts=self.nr, use_grid_fill=False)
                                for e in new_edges['geom_inner']:
                                    e.select = True

                        bm.verts.ensure_lookup_table()

                else:
                    self.report({"INFO"}, "Nothing selected?")
                    return {"CANCELLED"}

                bmesh.update_edit_mesh(me)

        if not sel_mode[0]:
            self.show_cuts = True
            bpy.ops.mesh.select_mode(type='EDGE')

        if single_edge:
            self.show_cuts = True

        return {'FINISHED'}


classes = (
    KeContextConnect,
)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
