from bpy.types import Operator
from bpy.props import BoolProperty


class KeModEmVis(Operator):
    bl_idname = "object.ke_mod_em_vis"
    bl_label = "Edit-Mode Visibility"
    bl_description = "Sets ALL modifiers Edit-Mode Visibility to OFF on selected objects\n(or ON,in redo panel)"
    bl_options = {'REGISTER', 'UNDO'}

    mode: BoolProperty(name="Modifiers Visibile", default=False,
                       description="Selected Objects: Sets ALL modifiers Edit Mode visibility to OFF\n"
                                   "(or ON,in redo panel)")

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.mode == "OBJECT"

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "GPENCIL":
                mods = obj.grease_pencil_modifiers
            else:
                mods = obj.modifiers
            if mods:
                for m in mods:
                    m.show_in_editmode = self.mode
        return {'FINISHED'}
