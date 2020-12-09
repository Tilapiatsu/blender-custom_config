bl_info = {
    "name": "Merge To Mouse",
    "author": "Kjell Emanuelsson 2019",
    "wiki_url": "http://artbykjell.com",
    "version": (1, 3, 5),
    "blender": (2, 80, 0),
}
import bpy
import bmesh
from mathutils import Vector
from bpy.types import Operator
from .ke_utils import get_loops, flatten, get_vert_nearest_mouse, get_area_and_type


class MESH_OT_merge_to_mouse(Operator):
    bl_idname = "mesh.merge_to_mouse"
    bl_label = "Merge to Mouse"
    bl_description = "Vert/Face Mode: Merge SELECTED vertices TO the selected (or edgelinked) vert CLOSEST to the Mouse Pointer. " \
                     "Edge Mode: Collapse SELECTED edges TO edge(s) CLOSEST to the Mouse Pointer"
    bl_options = {'REGISTER', 'UNDO'}

    mouse_pos = Vector((0, 0))

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
        areatype = get_area_and_type()[1]
        if areatype == "QUAD":
            bpy.ops.mesh.merge(type='LAST')
            return {'FINISHED'}

        obj = bpy.context.object
        obj_mtx = obj.matrix_world.copy()
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]
        edge_mode = False

        if sel_mode[1]:
            # Check for multiple edgeloops - or just vertcollapse, also tris...
            sel_edges = [e for e in bm.edges if e.select]

            if len(sel_edges) > 1:
                vps, tris = [], []
                for e in sel_edges:
                    vps.append(e.verts[:])
                    for f in e.link_faces:
                        if f not in tris:
                            if len(f.verts[:]) < 4:
                                tris.append(f)
                edge_loops = get_loops(vps)
                edge_loops = [i for i in edge_loops if i]
                if len(edge_loops) > 1 and not tris:
                    edge_mode = True

        if edge_mode:
            target_loop = []
            sel_verts = list(flatten(edge_loops))

            # my crappy loopsort fails on single edges sometimes?
            sel_verts_check = [v for v in bm.verts if v.select]
            if len(sel_verts_check) > len(sel_verts):
                error_sort = [i for i in sel_verts_check if i not in sel_verts]
                sel_verts = sel_verts_check
                edge_loops.append(error_sort)

            # find the target verts (to merge to)
            close_vert_candidate = get_vert_nearest_mouse(context, self.mouse_pos, sel_verts, obj_mtx)
            for i, el in enumerate(edge_loops):
                if close_vert_candidate in el:
                    target_loop = edge_loops.pop(i)

            # Get perpendicular merge loops (rows of verts to merge to target verts)
            vlink_edges = []
            for e in sel_edges:
                elf = e.link_faces[:]
                for f in elf:
                    fe = f.edges[:]
                    c = [i for i in fe if i in sel_edges]
                    if len(c) > 1:
                        perpendicular_edges = [i for i in fe if i not in sel_edges]
                        vlink_edges.append(perpendicular_edges)

            vlink_edges = list(flatten(vlink_edges))
            vps = [e.verts[:] for e in vlink_edges]
            vert_loops = get_loops(vps)

            merge_loops = []
            for target_v in target_loop:
                for vl in vert_loops:
                    verts = list(set(vl))
                    if target_v in verts:
                        vc = [i for i in verts if i != target_v]
                        vc = [target_v] + vc
                        merge_loops.append(vc)
                        break

            for mloop in merge_loops:
                # pos = obj_mtx @ mloop[0].co  # NO WORLDSPACE HERE, NO NO! ;D
                pos = mloop[0].co
                bmesh.ops.pointmerge(bm, verts=mloop, merge_co=pos)
                bmesh.update_edit_mesh(mesh)

            mesh.update()
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")

        else:
            sel = [v for v in bm.verts if v.select]
            if sel:
                bpy.context.tool_settings.mesh_select_mode = (True, False, False)
                sel_verts = []
                for v in sel:
                    for e in v.link_edges:
                        sel_verts.append(e.other_vert(v))

                sel_verts += sel
                sel_verts = list(set(sel_verts))

                merge_point = get_vert_nearest_mouse(context, self.mouse_pos, sel_verts, obj_mtx)

                if merge_point:
                    bm.select_history.add(merge_point)
                    bm.verts[merge_point.index].select = True
                    bpy.ops.mesh.merge(type='LAST', uvs=True)

                    bm.select_flush_mode()
                    bmesh.update_edit_mesh(obj.data, True)

        bpy.context.tool_settings.mesh_select_mode = (sel_mode[0], sel_mode[1], sel_mode[2])

        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
    MESH_OT_merge_to_mouse,
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
