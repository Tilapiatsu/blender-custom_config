import bmesh
import bpy
from bpy.props import EnumProperty
from bpy.types import Operator


class KeVertCountSelect(Operator):
    bl_idname = "view3d.ke_vert_count_select"
    bl_label = "Vert Count Select"
    bl_description = " Select geo by vert count in selected Object(s) in Edit or Object Mode. (Note: Ngons are 5+)"
    bl_options = {'REGISTER', 'UNDO'}

    sel_count: EnumProperty(
        items=[("0", "Loose Vert", "", 1),
               ("1", "Loose Edge", "", 2),
               ("2", "2 Edges", "", 3),
               ("3", "Tri", "", 4),
               ("4", "Quad", "", 5),
               ("5", "Ngon", "", 6)],
        name="Select Geo by Vert Count",
        default="3")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):
        nr = int(self.sel_count)
        sel_obj = [o for o in context.selected_objects if o.type == "MESH"]

        if not sel_obj:
            self.report({"INFO"}, "Object must be selected!")
            return {"CANCELLED"}

        if context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='DESELECT')

        for o in sel_obj:
            me = o.data
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()
            selection = []

            if nr <= 2:
                bm.select_mode = {'VERT'}
                for v in bm.verts:
                    le = len(v.link_edges)
                    if le == nr:
                        selection.append(v)

            elif nr >= 3:
                bm.select_mode = {'FACE'}
                for p in bm.faces:
                    pv = len(p.verts)
                    if nr == 5 and pv >= nr:
                        selection.append(p)
                    elif pv == nr:
                        selection.append(p)

            if selection:
                for v in selection:
                    v.select = True

            bm.select_flush_mode()
            bmesh.update_edit_mesh(o.data)

        if nr >= 3:
            context.tool_settings.mesh_select_mode = (False, False, True)
        else:
            context.tool_settings.mesh_select_mode = (True, False, False)

        return {'FINISHED'}
