from bpy.types import Operator


class KeShowCutterMod(Operator):
    bl_idname = "object.ke_showcuttermod"
    bl_label = "Show Cutter Modifier"
    bl_description = "Sets object using cutter (in boolean modifier) as active +\n" \
                     "Shows the modifier panel & sets the boolean Modifier as active.\n" \
                     "If many objects use the cutter: run again to cycle objects\n" \
                     "Note: No actual selection, only 'Active' status in outliner"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        cutter = context.object
        # cheezy re-select for cycling (which ofc does not work if cutters display are normal)
        if cutter not in context.selected_objects:
            candidates = [o for o in context.selected_objects if o.display_type in {"WIRE", "BOUNDS"}]
            if candidates:
                cutter = candidates[0]
                cutter.select_set(True)
                context.view_layer.objects.active = cutter

        objects_using_cutter = []
        modifiers_using_cutter = []
        obj_to_select = None
        custom_prop = False

        for k in cutter.keys():
            if k == 'kekit_cuttermod':
                custom_prop = True

        for o in context.view_layer.objects:
            mods = []
            for m in o.modifiers:
                if m.type == "BOOLEAN":
                    if m.object == cutter:
                        mods.append(m)
            if mods:
                objects_using_cutter.append(o)
                modifiers_using_cutter.extend(mods)

        if objects_using_cutter:
            obj_to_select = objects_using_cutter[0]

        if len(objects_using_cutter) > 1:
            if custom_prop:
                stored_objects = cutter['kekit_cuttermod']
                if not all(o in objects_using_cutter for o in stored_objects):
                    # stored list 'out of date'
                    stored_objects = objects_using_cutter
                # just shift stored list to cycle selection
                stored_objects.append(stored_objects.pop(0))
                # re-store & re-select
                cutter['kekit_cuttermod'] = stored_objects
                obj_to_select = stored_objects[0]
            else:
                cutter['kekit_cuttermod'] = objects_using_cutter

        if obj_to_select and modifiers_using_cutter:
            context.view_layer.objects.active = obj_to_select
            # Only outliner active mode, no seleciton, to make cycling multiple users work atm
            # ...and to see both cutter & target at the same time

            # Show the modifier in the properties tab (and expand)
            for m in obj_to_select.modifiers:
                m.show_expanded = False
                if m in modifiers_using_cutter:
                    m.is_active = True
                    m.show_expanded = True

        # Only open modifier tab if not already open
        p_area = None
        m_active = False
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.ui_type == 'PROPERTIES':
                    p_area = area
                    if area.spaces.active.context == 'MODIFIER':
                        m_active = True
                        area.tag_redraw()
        if not m_active and p_area:
            p_area.spaces.active.context = 'MODIFIER'
            p_area.tag_redraw()

        return {"FINISHED"}
