from math import sqrt

import bmesh
import bpy
from bpy.types import Operator


class KeFaceMatch(Operator):
    bl_idname = "mesh.ke_facematch"
    bl_label = "Scale From Face"
    bl_description = "Scales selected object(s) by the size(area) difference of selected faces to match last selected" \
                     "face\nSelect 1 Face per Object, in Multi-Edit mode\nScale will be auto-applied"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        if len(sel_objects) < 2:
            self.report({"INFO"}, "Invalid Selection (2+ Objects required)")
            return {"CANCELLED"}

        src_obj = context.object
        sel_obj = [o for o in sel_objects if o != src_obj]

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        bpy.ops.object.editmode_toggle()

        bma = bmesh.from_edit_mesh(src_obj.data)
        fa = [f for f in bma.faces if f.select]
        if fa:
            fa = fa[-1]
        else:
            self.report({"INFO"}, "Target Object has no selected face?")
            return {"CANCELLED"}

        ratio = 1

        for o in sel_obj:
            bmb = bmesh.from_edit_mesh(o.data)
            fb = [f for f in bmb.faces if f.select]
            if fb:
                fb = fb[-1]
                try:
                    ratio = sqrt(fa.calc_area() / fb.calc_area())
                except ZeroDivisionError:
                    self.report({"INFO"}, "Zero Division Error. Invalid geometry?")

                o.scale *= ratio

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        bpy.ops.object.editmode_toggle()

        return {"FINISHED"}
