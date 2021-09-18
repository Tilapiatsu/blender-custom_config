bl_info = {
    "name": "keUnbevel",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 1, 1),
    "blender": (2, 80, 0),
}

import bpy
import bmesh
from bpy.types import Operator
from .ke_utils import get_loops
# from mathutils import Vector, Matrix
from mathutils.geometry import intersect_line_line


class MESH_OT_ke_unbevel(Operator):
    bl_idname = "mesh.ke_unbevel"
    bl_label = "Unbevel"
    bl_description = "Un-bevel by selecting non-looping edges across the bevel. (2 end-edges per selection are the vectors)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        obj = bpy.context.active_object
        od = obj.data
        bm = bmesh.from_edit_mesh(od)
        sel_mode = bpy.context.tool_settings.mesh_select_mode[:]

        if sel_mode[1]:
            bm.edges.ensure_lookup_table()
            sel_edges = [e for e in bm.edges if e.select]
            vert_pairs = []
            for e in sel_edges:
                vp = [v for v in e.verts]
                vert_pairs.append(vp)

            loops = get_loops(vert_pairs, legacy=True)

            bpy.ops.mesh.select_mode(type='VERT')

            for loop in loops:
                bm.verts.ensure_lookup_table()
                bpy.ops.mesh.select_all(action='DESELECT')

                v1, v2, v3, v4 = loop[0].co, loop[1].co, loop[-1].co, loop[-2].co
                xpoint = intersect_line_line(v1, v2, v3, v4)[0]
                merge_point = loop[1]
                merge_point.co = xpoint

                merge_verts = loop[1:-1]
                for v in merge_verts:
                    bm.verts[v.index].select = True

                bm.select_history.add(merge_point)
                bm.verts[merge_point.index].select = True
                bpy.ops.mesh.merge(type='LAST', uvs=True)

            bm.normal_update()
            bmesh.update_edit_mesh(od)
            bpy.ops.mesh.select_mode(type='EDGE')

        else:
            self.report({"INFO"}, "Selection Mode Error: Please use EDGE selection.")

        return {"FINISHED"}

# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------

def register():
    bpy.utils.register_class(MESH_OT_ke_unbevel)

def unregister():
    bpy.utils.unregister_class(MESH_OT_ke_unbevel)

if __name__ == "__main__":
    register()
