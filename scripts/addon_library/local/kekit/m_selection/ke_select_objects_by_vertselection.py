import bpy
from bpy.types import Operator


class KeVertObjectSelect(Operator):
    bl_idname = "object.ke_select_objects_by_vertselection"
    bl_label = "Select Objects by VertSelection"
    bl_description = "In Multi-Object Edit Mode:\n" \
                     "Selects only objects that have vertices selected, and set object mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def execute(self, context):
        og_mode = str(context.mode)
        if og_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        sel = [o for o in context.selected_objects if o.type == "MESH"]
        new_sel = []
        for o in sel:
            s = [0] * len(o.data.vertices)
            o.data.vertices.foreach_get('select', s)
            if any(s):
                new_sel.append(o)

        bpy.ops.object.select_all(action="DESELECT")
        for o in new_sel:
            o.select_set(True)

        return {"FINISHED"}
