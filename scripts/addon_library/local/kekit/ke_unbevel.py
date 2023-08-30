import bpy
import bmesh
from bpy.types import Operator
from ._utils import vertloops, flattened, get_face_islands
from mathutils.geometry import intersect_line_line
from mathutils import Vector


def get_endpoints(vert, exclude_faces, vec_check, se):
    vert_linkfaces = [i for i in vert.link_faces if i not in exclude_faces]
    ce = [None, -9]
    ngon = False
    # unconnected tri, ngon cyl caps etc
    if vert_linkfaces:
        ngon = all(len(f.verts) != 4 for f in vert_linkfaces)
        if len(vert_linkfaces) == 1 and len(vert_linkfaces[0].verts) != 4:
            ngon = True
    if ngon:
        return vert.co, vert_linkfaces[0].calc_center_median_weighted(), True
    else:
        for f in vert_linkfaces:
            edge_candidates = [e for e in f.edges if e not in se]
            if edge_candidates:
                for e in edge_candidates:
                    if vert in e.verts:
                        vec = Vector(e.verts[0].co - e.verts[1].co).normalized()
                        cv = abs(vec.dot(vec_check)) - 1
                        if cv > ce[1]:
                            ce = [e, cv]
        if ce[0] is not None:
            return vert.co, ce[0].other_vert(vert).co, False
    return None, None, False


class KeUnbevel(Operator):
    bl_idname = "mesh.ke_unbevel"
    bl_label = "Unbevel"
    bl_description = "Select the Edge Ring(s) on bevel(s)\n" \
                     "Rebevel: Adjust settings in redo-panel"
    bl_options = {'REGISTER', 'UNDO'}

    rebevel: bpy.props.BoolProperty(name="Rebevel", default=False)
    keep_width: bpy.props.BoolProperty(name="Keep Width", default=True)
    offset: bpy.props.FloatProperty(name="Offset", min=0, max=100, default=0.01, subtype="DISTANCE")
    segments: bpy.props.IntProperty(name="Rebevel Count", min=0, max=999, soft_max=99, default=0)
    profile: bpy.props.FloatProperty(name="Rebevel Profile", min=0, max=1, default=0.5)
    merge_uvs: bpy.props.BoolProperty(default=False, name="Rebevel Merge UVs", description="You rarely want this")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.use_property_split = True
        layout.prop(k, "unbevel_autoring", text="Auto Ring Select", toggle=True)
        row = layout.row(align=True)
        row.prop(self, "rebevel", toggle=True)
        if self.rebevel:
            row.prop(self, "keep_width", toggle=True)
            if not self.keep_width:
                layout.prop(self, "offset", toggle=True)
            layout.prop(self, "segments")
            layout.prop(self, "profile")
            layout.prop(self, "merge_uvs", toggle=True)
        layout.separator()

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        od = obj.data
        bm = bmesh.from_edit_mesh(od)
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        sel_faces = [i for i in bm.faces if i.select]

        if sel_mode[2]:
            edge_rings = []

            face_island = get_face_islands(bm, sel_faces=sel_faces)

            for island in face_island:
                # sort for edge rings
                outer_edges = []
                inner_edges = []

                for f in island:
                    for of in island:
                        if of != f:
                            for e in f.edges:
                                if e in of.edges:
                                    inner_edges.append(e)
                                else:
                                    outer_edges.append(e)

                outer_edges = list(set(outer_edges))
                inner_edges = list(set(inner_edges))
                inner_verts = flattened([e.verts for e in inner_edges])
                for e in outer_edges:
                    if any(v for v in e.verts if v in inner_verts) and e not in inner_edges:
                        edge_rings.append(e)

            if edge_rings:
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                bpy.ops.mesh.select_all(action="DESELECT")
                for e in edge_rings:
                    e.select_set(True)
                bmesh.update_edit_mesh(od)

        if context.preferences.addons[__package__].preferences.unbevel_autoring:
            bpy.ops.mesh.loop_multi_select(ring=True)

        sel_edges = [i for i in bm.edges if i.select]

        if not sel_edges:
            self.report({"INFO"}, "Invalid selection")
            return {"CANCELLED"}

        # compensation for rebevel clamp-filling up old bevel width
        seg_count = self.segments + 1

        post_sel = []
        post_merge = []

        vert_pairs = [e.verts for e in sel_edges]
        loops = vertloops(vert_pairs)

        if len(sel_edges) == len(loops) and self.rebevel:
            # Chamfer special, needs a center cut
            geo = bmesh.ops.bisect_edges(bm, edges=sel_edges, cuts=2)
            sel_verts = [i for i in geo['geom_split'] if isinstance(i, bmesh.types.BMVert)]
            sel_edges = [i for i in geo['geom_split'] if isinstance(i, bmesh.types.BMEdge)]
            bmesh.ops.connect_verts(bm, verts=sel_verts)
            vert_pairs = [e.verts for e in sel_edges]
            loops = vertloops(vert_pairs)

        exclude = []
        for e in sel_edges:
            exclude.extend(e.link_faces[:])
        exclude = list(set(exclude))

        mvs = []
        for vloop in loops:
            # create in-loop end vectors to test for closest
            vc1 = Vector(vloop[0].co - vloop[1].co).normalized()
            vc2 = Vector(vloop[-1].co - vloop[-2].co).normalized()

            v1, v2, ngon1_2 = get_endpoints(vert=vloop[0], exclude_faces=exclude, vec_check=vc1, se=sel_edges)
            v3, v4, ngon3_4 = get_endpoints(vert=vloop[-1], exclude_faces=exclude, vec_check=vc2, se=sel_edges)

            if any(i is None for i in [v1, v2, v3, v4]):
                self.report({"INFO"}, "Aborted: Invalid Selection")
                return {"CANCELLED"}

            linepoints = intersect_line_line(v1, v2, v3, v4)

            if linepoints is None:
                self.report({"INFO"}, "Aborted: Invalid Selection")
                return {"CANCELLED"}

            if ngon1_2 and ngon3_4:
                xpoint = linepoints[0].lerp(linepoints[-1], 0.5)
            elif ngon1_2:
                xpoint = linepoints[-1]
            elif ngon3_4:
                xpoint = linepoints[0]
            else:
                p1 = vc1.dot(Vector(vloop[0].co - linepoints[0]).normalized())
                p2 = vc1.dot(Vector(vloop[0].co - linepoints[-1]).normalized())
                if p1 > p2:
                    xpoint = linepoints[0]
                else:
                    xpoint = linepoints[-1]

            if self.rebevel and self.keep_width:
                merge_verts = vloop[1:-1]
            else:
                merge_verts = vloop

            mvs.append(merge_verts + [xpoint])
            post_merge.extend([vloop[0], vloop[-1]])

        for mv in mvs:
            post_sel.append(mv[0])
            bmesh.ops.pointmerge(bm, verts=mv[:-1], merge_co=mv[-1])

        bm.normal_update()
        bmesh.update_edit_mesh(od)

        bpy.ops.mesh.select_all(action="DESELECT")
        for v in post_sel:
            v.select_set(True)
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_mode(type='EDGE')

        if self.rebevel:
            new_edges = [e for e in bm.edges if e.select]
            if new_edges:
                if self.keep_width:
                    o = 100
                    t = "PERCENT"
                else:
                    o = self.offset
                    t = "WIDTH"
                result = bmesh.ops.bevel(bm, geom=new_edges, offset_type=t, offset=o, affect="EDGES",
                                         clamp_overlap=True, loop_slide=True, segments=seg_count, profile=self.profile)
                if self.keep_width:
                    merge = result["verts"] + post_merge
                    bmesh.ops.remove_doubles(bm, verts=merge, dist=0.0003)
                bmesh.update_edit_mesh(od)
            else:
                self.report({"INFO"}, "Aborted Rebevel: Ops Selection Error")

        if sel_mode[2]:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        return {"FINISHED"}


#
# CLASS REGISTRATION
#
def register():
    bpy.utils.register_class(KeUnbevel)


def unregister():
    bpy.utils.unregister_class(KeUnbevel)
