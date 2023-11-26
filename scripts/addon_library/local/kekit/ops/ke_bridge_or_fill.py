import bmesh
import bpy
from bpy.types import Operator
from mathutils import Vector
from .._utils import vertloops


def normal_flip(context, obj, bm, mesh):
    rm = context.space_data.region_3d.view_matrix
    v = Vector(rm[2])
    bmesh.update_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    new_face = [f for f in bm.faces if f.select]
    if new_face:
        f_normal = obj.matrix_world @ new_face[-1].normal
        if f_normal.dot(v) < 0:
            new_face[-1].normal_flip()
            bmesh.update_edit_mesh(mesh)


class KeBridgeOrFill(Operator):
    bl_idname = "mesh.ke_bridge_or_fill"
    bl_label = "Bridge or Fill"
    bl_description = "BRIDGE Non-continous Edges (or opposite Faces) selected\n" \
                     "GRID-FILL: 1 continous border Edge Loop selected\n" \
                     "F2: 1 Edge or 1 Vert selected\n" \
                     "FACE ADD: 2 Edges (connected) or 3+ verts in vert mode\n" \
                     "Floaters: New Edge/Face from selected"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]

        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.verts.ensure_lookup_table()

        sel_verts = [v for v in bm.verts if v.select]
        sel_edges = [e for e in bm.edges if e.select]

        if sel_verts:
            floater = not any([i for j in [v.link_faces for v in sel_verts] for i in j])
        else:
            self.report({"INFO"}, "Nothing selected?")
            return {"CANCELLED"}

        if sel_mode[0]:

            if len(sel_verts) == 1:
                # Single vert - F2 mode
                try:
                    bpy.ops.mesh.f2('INVOKE_DEFAULT')
                except Exception as e:
                    print("F2 aborted - using Mesh Fill:\n", e)
                    bpy.ops.mesh.fill('INVOKE_DEFAULT')
            else:
                # 'Add Edge/Face to selected' (verts) mode
                bpy.ops.mesh.edge_face_add()
                normal_flip(context, obj, bm, mesh)

        elif sel_mode[1] and sel_edges:

            if floater and len(sel_edges) > 1:
                # 'Add Edge/Face to selected' (floater edges) mode
                bpy.ops.mesh.edge_face_add()
                normal_flip(context, obj, bm, mesh)

            else:
                if len(sel_edges) == 1:
                    # Single edge - F2 mode
                    try:
                        bpy.ops.mesh.f2('INVOKE_DEFAULT')
                    except Exception as e:
                        print("F2 aborted - using Mesh Fill:\n", e)
                        bpy.ops.mesh.fill('INVOKE_DEFAULT')
                else:
                    # Check if edges are a loop or not
                    vert_pairs = []
                    for e in sel_edges:
                        vp = [v for v in e.verts]
                        vert_pairs.append(vp)

                    check_loops = vertloops(vert_pairs)

                    if len(check_loops) == 1 and check_loops[0][0] == check_loops[-1][-1] and len(sel_edges) % 2 == 0:
                        # Even edges loop, try grid for nice quads
                        try:
                            bpy.ops.mesh.fill_grid('INVOKE_DEFAULT', True)
                        except Exception as e:
                            print("Fill Grid aborted - using F2 or Mesh Fill:\n", e)
                            try:
                                bpy.ops.mesh.f2('INVOKE_DEFAULT')
                            except Exception as e:
                                print("F2 aborted - using Mesh Fill:\n", e)
                                bpy.ops.mesh.fill('INVOKE_DEFAULT')

                    elif len(check_loops) == 1:
                        # Un-even edge count loop, add ngon to avoid triangulation
                        bpy.ops.mesh.edge_face_add()
                    else:
                        # No loop - Bridging
                        if len(sel_edges) % 2 != 0:
                            bpy.ops.mesh.fill('INVOKE_DEFAULT')
                        else:
                            try:
                                bpy.ops.mesh.bridge_edge_loops('INVOKE_DEFAULT', True)
                            except Exception as e:
                                print("Bridge Edge Loops aborted: \n", e)

        elif sel_mode[2]:
            sel_faces = [f for f in bm.faces if f.select]
            if sel_faces:
                bpy.ops.mesh.bridge_edge_loops()

        return {'FINISHED'}
