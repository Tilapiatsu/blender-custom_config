import bpy
from bpy.types import Operator
from .._utils import get_prefs


class KeShadingToggle(Operator):
    bl_idname = "view3d.ke_shading_toggle"
    bl_label = "Shading Toggle"
    bl_description = "Toggles selected object(s) between Flat & Smooth shading.\nAlso works in Edit mode."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        aso = []
        cm = str(context.mode)
        k = get_prefs()
        tri_mode = k.shading_tris

        if cm != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
            if cm == "EDIT_MESH":
                cm = "EDIT"

        for obj in context.selected_objects:
            try:
                current = obj.data.polygons[0].use_smooth
            except AttributeError:
                self.report({"WARNING"}, "Invalid Object selected for Smooth/Flat Shading Toggle - Cancelled")
                return {"CANCELLED"}

            if tri_mode:
                tmod = None
                mindex = len(obj.modifiers) - 1
                for m in obj.modifiers:
                    if m.name == "Triangulate Shading":
                        tmod = m
                        if current is False:
                            bpy.ops.object.modifier_remove(modifier="Triangulate Shading")
                        else:
                            bpy.ops.object.modifier_move_to_index(modifier="Triangulate Shading", index=mindex)

                if tmod is None and current:
                    obj.modifiers.new(name="Triangulate Shading", type="TRIANGULATE")

            val = [not current]
            values = val * len(obj.data.polygons)
            obj.data.polygons.foreach_set("use_smooth", values)
            obj.data.update()

            if not current:
                mode = " > Smooth"
            else:
                mode = " > Flat"
            aso.append(obj.name + mode)

        bpy.ops.object.mode_set(mode=cm)

        if len(aso) > 5:
            t = "%s objects" % str(len(aso))
        else:
            t = ", ".join(aso)
        self.report({"INFO"}, "Toggled: %s" % t)

        return {"FINISHED"}
