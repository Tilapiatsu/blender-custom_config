import bpy
from bpy.types import Operator


class KeCheckOriginAtVert(Operator):
    bl_idname = "view3d.ke_check_origin_at_vert"
    bl_label = "Check Origin at Vert"
    bl_description = ("Check if selected object(s) origin does (not) share coordinates with any of its vertices\n"
                      "See Console Output for per-object report")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == "OBJECT"

    def execute(self, context):
        sel = list(context.selected_objects)
        if not sel:
            sel = [context.object]

        bpy.ops.object.select_all(action="DESELECT")
        rn = 4
        not_snapped = []
        multiple = []
        print("Check Origin at Vertex:")

        for obj in sel:
            x = round(obj.location.x, rn)
            y = round(obj.location.y, rn)
            z = round(obj.location.z, rn)
            match = 0

            for v in obj.data.vertices:
                co = obj.matrix_world @ v.co
                mv = 0
                if x == round(co[0], rn):
                    mv += 1
                if y == round(co[1], rn):
                    mv += 1
                if z == round(co[2], rn):
                    mv += 1
                if mv == 3:
                    match += 1

            marker = ""
            if not match:
                not_snapped.append(obj)
                obj.select_set(True)
                marker = " [!] "

            multi = ""
            if match > 1:
                multiple.append(obj)
                multi = "- Note: Object has more than one (%i) vertices at Origin location" % match

            # Single object report:
            print(obj.name, "%s" % marker, bool(match), multi)

        # Summary
        if not_snapped:
            self.report({"INFO"}, "%i Object(s) Origin(s) NOT snapped to vertex" % (len(not_snapped)))
        else:
            self.report({"INFO"}, "%i Object(s) Origin(s) snapped to vertex" % (len(not_snapped)))

        return {'FINISHED'}
