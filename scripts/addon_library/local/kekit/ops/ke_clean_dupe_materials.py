import bpy
import sys
from bpy.types import Operator
from .._utils import refresh_ui


class KeCleanDupeMaterials(Operator):
    bl_idname = "object.ke_clean_dupe_materials"
    bl_label = "Clean Dupe Materials"
    bl_description = "Finds duplicate (*.001 etc.) materials in selected objects & assigns the original material\n" \
                     "Do NOT use if you want to KEEP materials ending with .001, .99999 etc. (dot + any number)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == "OBJECT"

    def execute(self, context):
        report = ["\nClean Dupe Materials:"]

        for o in context.selected_editable_objects:
            if o.material_slots == 0:
                continue
            report.append("\n%s:" % o.name)

            for slot in o.material_slots:
                if slot.material:
                    s = slot.material.name
                    report.append(" %s" % s)

                    og = None
                    nr = []
                    if "." in s:
                        try:
                            nr = [int(i) for i in s.split(".")[-1]]
                        except ValueError:
                            continue
                        if len(nr) >= 3:
                            og = s.split(".")[0]

                    if og and nr:
                        if og in bpy.data.materials:
                            o.data.materials[slot.slot_index] = bpy.data.materials[og]
                            report.append("->%s " % og)

        for i in report:
            sys.stdout.write(i)
        sys.stdout.write("\n\n")
        sys.stdout.flush()
        refresh_ui()
        return {"FINISHED"}
