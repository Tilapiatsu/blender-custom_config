from bpy.types import Operator


class KeToggleModVis(Operator):
    bl_idname = "view3d.ke_toggle_mod_vis"
    bl_label = "Toggle Modifier Visibility"
    bl_description = ("Toggles ALL (active or selected objects) modifiers viewport visibility\n"
                      "Tip: If ANY modifier is OFF - all will be set to OFF. Run again to invert.")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if context.selected_objects:
            objects = list(context.selected_objects)
        else:
            objects = [context.active_object]

        for obj in objects:
            # from addon tools: avoid toggling not exposed modifiers (Collision, see T53406)
            skip_type = "COLLISION"
            # check if the active object has only one non-exposed modifier as the logic will fail
            if len(obj.modifiers) == 1 and \
                    obj.modifiers[0].type in skip_type:
                continue

            if obj.type == "GPENCIL":
                mods = obj.grease_pencil_modifiers
            else:
                mods = obj.modifiers
            if mods:
                action = True
                if any([m for m in mods if m.show_viewport]):
                    action = False
                for m in mods:
                    if m.type == skip_type:
                        continue
                    m.show_viewport = action

        return {'FINISHED'}
