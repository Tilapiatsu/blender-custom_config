import bmesh
import bpy
from bpy.types import Operator
from .._utils import is_bmvert_collinear


class KeSelectCollinear(Operator):
    bl_idname = "mesh.ke_select_collinear"
    bl_label = "Select Collinear Verts"
    bl_description = "Selects Collinear Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]
        obj = context.active_object
        if not obj:
            obj = sel_obj[0]

        og_mode = [b for b in context.tool_settings.mesh_select_mode]
        context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action='DESELECT')

        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.verts.ensure_lookup_table()
        bm.select_mode = {'VERT'}

        count = 0
        for v in bm.verts:
            if is_bmvert_collinear(v):
                v.select = True
                count += 1

        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)

        if count > 0:
            self.report({"INFO"}, "Total Collinear Verts Found: %s" % count)
        else:
            context.tool_settings.mesh_select_mode = og_mode
            self.report({"INFO"}, "No Collinear Verts Found")

        return {"FINISHED"}
