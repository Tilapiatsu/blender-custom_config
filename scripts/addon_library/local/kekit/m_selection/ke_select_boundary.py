import bmesh
import bpy
from bpy.types import Operator


class KeSelectBoundary(Operator):
    bl_idname = "mesh.ke_select_boundary"
    bl_label = "select boundary(+active)"
    bl_description = "Select Boundary edges & sets one edge active\n" \
                     "Run again on a selected boundary to toggle to inner region selection\n" \
                     "Nothing selected = Selects all -border- edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        og_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        if obj is None:
            obj = context.object

        bm = bmesh.from_edit_mesh(obj.data)

        sel_verts = [v for v in bm.verts if v.select]
        og_edges = [e for e in bm.edges if e.select]

        if len(sel_verts) == 0:
            bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.region_to_loop()

        sel_edges = [e for e in bm.edges if e.select]

        if sel_edges:
            sel_check = [e for e in bm.edges if e.select]
            toggle = set(og_edges) == set(sel_check)

            if toggle:
                bpy.ops.mesh.loop_to_region()

            bm.select_history.clear()
            bm.select_history.add(sel_edges[0])
        else:
            context.tool_settings.mesh_select_mode = og_mode

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}
