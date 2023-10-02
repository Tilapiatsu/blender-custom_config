import bmesh
import bpy
from bpy.types import Operator
from .._utils import vertloops


class KeBridgeOrFill(Operator):
    bl_idname = "mesh.ke_bridge_or_fill"
    bl_label = "Bridge or Fill"
    bl_description = "BRIDGE Non-continous Edges selected\n" \
                     "GRID-FILL: 1 continous border Edge Loop selected\n" \
                     "F2: 1 Edge or 1 Vert selected\n" \
                     "FACE ADD: 2 Edges (connected) or 3+ verts in vert mode"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_mode = context.tool_settings.mesh_select_mode[:]

        obj = context.active_object
        mesh = obj.data
        obj.update_from_editmode()

        if sel_mode[0]:
            sel_verts = [v for v in mesh.vertices if v.select]
            if len(sel_verts) == 1:
                try:
                    bpy.ops.mesh.f2('INVOKE_DEFAULT')
                except Exception as e:
                    print("F2 aborted - using Mesh Fill:\n", e)
                    bpy.ops.mesh.fill('INVOKE_DEFAULT')
            elif len(sel_verts) > 2:
                bpy.ops.mesh.edge_face_add()

        if sel_mode[1]:
            vert_pairs = []
            sel_edges = [e for e in mesh.edges if e.select]
            for e in sel_edges:
                vp = [v for v in e.vertices]
                vert_pairs.append(vp)

            if len(sel_edges) == 1:
                try:
                    bpy.ops.mesh.f2('INVOKE_DEFAULT')
                except Exception as e:
                    print("F2 aborted - using Mesh Fill:\n", e)
                    bpy.ops.mesh.fill('INVOKE_DEFAULT')

            elif vert_pairs:
                if len(sel_edges) == 2:
                    tri_check = len(list(set(vert_pairs[0] + vert_pairs[1])))
                    if tri_check < 4:
                        bm = bmesh.from_edit_mesh(mesh)
                        bm.verts.ensure_lookup_table()
                        sel_verts = [v for v in bm.verts if v.select]
                        new = bm.faces.new([bm.verts[i.index] for i in sel_verts])
                        uv_layer = bm.loops.layers.uv.verify()
                        for loop in new.loops:
                            loop_uv = loop[uv_layer]
                            loop_uv.uv[0] = loop.vert.co.x + 0.5
                            loop_uv.uv[1] = loop.vert.co.y + 0.5
                        bmesh.update_edit_mesh(mesh)

                check_loops = vertloops(vert_pairs)
                if len(check_loops) == 1 and check_loops[0][0] == check_loops[-1][-1] and len(sel_edges) % 2 == 0:
                    try:
                        bpy.ops.mesh.fill_grid('INVOKE_DEFAULT', True)
                    except Exception as e:
                        print("Fill Grid aborted - using F2 or Mesh Fill:\n", e)
                        try:
                            bpy.ops.mesh.f2('INVOKE_DEFAULT')
                        except Exception as e:
                            print("F2 aborted - using Mesh Fill:\n", e)
                            bpy.ops.mesh.fill('INVOKE_DEFAULT')
                else:
                    if len(sel_edges) % 2 != 0:
                        bpy.ops.mesh.fill('INVOKE_DEFAULT')
                    else:
                        try:
                            bpy.ops.mesh.bridge_edge_loops('INVOKE_DEFAULT', True)
                        except Exception as e:
                            print("Bridge Edge Loops aborted: \n", e)

        return {'FINISHED'}
