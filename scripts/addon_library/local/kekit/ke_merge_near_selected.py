import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from ._utils import get_distance


class KeMergeNearSelected(Operator):
    bl_idname = "mesh.ke_merge_near_selected"
    bl_label = "Merge Near Selected"
    bl_description = "Merges other verts near selected verts to them (in any element mode!)\n" \
                     "at set link-depth and distance"
    bl_options = {'REGISTER', 'UNDO'}

    distance : bpy.props.FloatProperty(min=0, max=99, default=0.01, name="Distance", step=0.001, precision=5,
                                       description="Distance from each vert to merge linked verts from")
    link_level : bpy.props.IntProperty(min=1, max=99, default=1, name="Link Level",
                                       description="The # of edge links away from each vert to process distance on")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        if context.object.scale != Vector((1.0, 1.0, 1.0)):
            self.report({"INFO"}, "Scale is not applied - Results may be unpredictable")

        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)

        sel_verts = [v for v in bm.verts if v.select]

        if not sel_verts:
            self.report({"INFO"}, "No elements selected?")
            return {"CANCELLED"}

        # 1/2 - Get linked verts and merge them at sel_vert co - except the sel_vert, avoiding dead index nonsense
        # todo: make less crazy brutal for-loop process? Nah...
        for v in sel_verts:
            mergeverts = [v]

            for i in range(0, self.link_level):
                lvs = []

                for linkvert in mergeverts:
                    for e in linkvert.link_edges:
                        ov = e.other_vert(linkvert)
                        d = get_distance(v.co, ov.co)

                        if d < self.distance:
                            other_edgevert_closer = False
                            # Check if any other sel_vert is closer 1st
                            for ole in ov.link_edges:
                                olev = ole.other_vert(ov)
                                if olev in sel_verts and olev != ov:
                                    od = get_distance(olev.co, ov.co)
                                    if od < d:
                                        other_edgevert_closer = True
                                        break

                            if not other_edgevert_closer:
                                lvs.append(ov)
                            else:
                                break

                    lvs = list(set(lvs))
                mergeverts.extend(lvs)

            mergeverts = list(set(mergeverts) - set(sel_verts))
            if mergeverts:
                bmesh.ops.pointmerge(bm, verts=mergeverts, merge_co=v.co[:])

        bmesh.update_edit_mesh(mesh)

        # 2/2 - And then merge the selverts+linked to avoid processing the whole mesh:
        bm.verts.ensure_lookup_table()
        sel_verts = [v for v in bm.verts if v.select]

        linkverts = []
        for v in sel_verts:
            for e in v.link_edges:
                linkverts.extend(e.verts[:])
            linkverts.append(v)
        linkverts = list(set(linkverts))

        md = 0.0001
        if self.distance < md:
            md = self.distance
        bmesh.ops.remove_doubles(bm, verts=linkverts, dist=md)

        bmesh.update_edit_mesh(mesh)
        mesh.update()

        return {'FINISHED'}


#
# CLASS REGISTRATION
#
classes = (KeMergeNearSelected,)

modules = ()


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
