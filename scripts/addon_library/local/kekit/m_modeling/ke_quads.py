import bmesh
import bpy
from bpy.types import Operator


def get_shared_edges(f, otherset):
    shared = []
    for of in otherset:
        if of.is_valid and f.is_valid:
            if of != f:
                shared.extend([e for e in f.edges if e in of.edges])
    return shared


class KeQuads(Operator):
    bl_idname = "mesh.ke_quads"
    bl_label = "Quads"
    bl_description = "Converts selected triangles & ngons to quads.\n" \
                     "Note: Not intended for cylinder-end type ngons"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        # SETUP
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        sel_faces = [f for f in bm.faces if f.select]

        # (SLOWLY) PROCESSING EACH NGON (TO AVOID BORDER ISSUES)
        for f in sel_faces:
            if len(f.verts) > 4:
                # 1ST TRIANGULATE NGON
                ret = bmesh.ops.triangulate(bm, faces=[f], quad_method='BEAUTY', ngon_method='BEAUTY')
                faces = ret["faces"]
                del ret
                bm.faces.ensure_lookup_table()

                # SORT NGON-TRIS BY SHARED EDGE COUNT
                center_tris = []
                outer_tris = []
                for tri in faces:
                    shared_edges = get_shared_edges(tri, faces)
                    if len(shared_edges) > 1:
                        center_tris.append(tri)
                    else:
                        outer_tris.append(tri)

                # DISSOLVE 'OUTWARDS' FROM CENTER NGON-TRIS
                for t in center_tris:
                    shared_edges = get_shared_edges(t, outer_tris)
                    if len(shared_edges) < 2:
                        bmesh.ops.dissolve_edges(bm, edges=shared_edges, use_verts=False, use_face_split=False)

                bmesh.update_edit_mesh(obj.data)

        # CLEANUP TRIANGULATED QUADS
        bpy.ops.mesh.tris_convert_to_quads()

        return {"FINISHED"}
