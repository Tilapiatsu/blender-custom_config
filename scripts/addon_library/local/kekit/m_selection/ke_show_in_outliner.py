import bpy
from bpy.types import Operator


class KeShowInOutliner(Operator):
    bl_idname = "view3d.ke_show_in_outliner"
    bl_label = "Show in Outliner"
    bl_description = "[keKit] Locate the selected object(s) in the outliner (& set parent Collection as Active)\n" \
                     "(in Object Context Menu)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        override = None
        for area in context.screen.areas:
            if 'OUTLINER' in area.type:
                for region in area.regions:
                    if 'WINDOW' in region.type:
                        override = {'area': area, 'region': region}
                        break
                break

        if not sel_objects or override is None:
            self.report({"INFO"}, "Nothing selected? / Outliner not found?")
            return {"CANCELLED"}

        for obj in sel_objects:
            context.view_layer.objects.active = obj
            bpy.ops.outliner.show_active(override)

        return {"FINISHED"}
