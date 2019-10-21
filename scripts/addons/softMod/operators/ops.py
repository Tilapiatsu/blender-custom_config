import bpy


from ..api.object_handlers import SoftWidgetHandler, SoftDeformedHandler

class OT_delete_override(bpy.types.Operator):
    """ Override delete action
    """
    bl_idname = "object.delete_custom"
    bl_label = "Delete sofmods"
    bl_description = "Cleaner way to delete softmods"


    # use_global = BoolProperty(default = False)
    # confirm = BoolProperty(default = False)
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):

        selection = bpy.context.selected_objects
        widgets=[]
        for selected in selection:

            widget = SoftWidgetHandler.from_widget(selected)
            if widget:
                widget.delete()


        return {'FINISHED'}

class OT_paint_mode(bpy.types.Operator):
    """ Override delete action
    """
    bl_idname = "object.softmod_paint"
    bl_label = "Paint Soft Mod"
    bl_description = "Alt+Click to paint the mirror group."


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def invoke(self , context , event):

        if event.alt:
            self.paint_mode(context, mirror= True)

        else:
            self.paint_mode (context , mirror=False)

        return {'FINISHED'}

    def paint_mode(self, context, mirror):
        active = bpy.context.active_object
        widget = SoftWidgetHandler.from_widget(active)
        if widget:
            widget.paint_mode(mirror = mirror)
            return {"FINISHED"}


        return {'FINISHED'}

class OT_toggle_soft_mod(bpy.types.Operator):
    bl_idname = "object.softmod_toggle"
    bl_label = "Toggle Soft Mod"
    bl_description = "Toggle on and off the selected widget"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):
        selection = bpy.context.selected_objects

        widgets=[]
        for selected in selection:
            widget = SoftWidgetHandler.from_widget(selected)
            if widget:
                widgets.append(widget)
        state= not widgets[0].show_viewport
        for widget in widgets:
            widget.show_viewport = state


        return {'FINISHED'}




class OT_parent_widget(bpy.types.Operator):
    """ Override delete action
    """
    bl_idname = "object.parent_widget"
    bl_label = "Parent widget"

    bl_description = "Parent widget to object"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):
        parent = bpy.context.active_object

        selection = bpy.context.selected_objects
        widgets=[]
        for selected in selection:
            if selected == parent:
                continue
            widget = SoftWidgetHandler.from_widget(selected)
            if widget:
                widgets.append(widget)
        if widgets:
            for widget in widgets:
                widget.parent_to(parent)


        return {'FINISHED'}

class OT_unparent_widget(bpy.types.Operator):
    """ Override delete action
    """
    bl_idname = "object.unparent_widget"
    bl_label = "Unparent widget"

    bl_description = "Remove parent from widget"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):

        selection = bpy.context.selected_objects
        widgets=[]
        for selected in selection:
            widget = SoftWidgetHandler.from_widget(selected)
            if widget:
                widgets.append(widget)
        if widgets:
            for widget in widgets:
                widget.unparent()


        return {'FINISHED'}

class OT_rename_softMod(bpy.types.Operator):

    bl_idname = "object.rename_softmod"
    bl_label = "rename softMod"

    bl_description = "Rename current sofMod"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):

        active = bpy.context.active_object
        widget = SoftWidgetHandler.from_widget(active)
        new_name = bpy.context.scene.soft_mod.widget_name
        widget.rename(new_name)


        return {'FINISHED'}

class OT_convert_to_shape_key(bpy.types.Operator):

    bl_idname = "object.convert_widget_to_shape_key"
    bl_label = "Convert softMod to shape key"

    bl_description = "Convert selected widgets into shape keys"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):

        selection = bpy.context.selected_objects
        widgets=[]
        for selected in selection:
            widget = SoftWidgetHandler.from_widget(selected)
            if widget:
                widgets.append(widget)
        if widgets:
            deformed_mods = {}
            deformed_list= []
            for widget in widgets:

                deformed = widget.deformed
                mod = widget.armature.modifier
                if deformed.name not in deformed_mods.keys():
                    deformed_mods[deformed.name] = []
                    deformed_list.append(deformed)
                deformed_mods[deformed.name].append(mod)

            for deformed in deformed_list:
                mods = deformed_mods[deformed.name]
                deformed.mods_to_shape_keys(mods)

        return {'FINISHED'}

class OT_deformed_to_shape_key(bpy.types.Operator):

    bl_idname = "object.convert_to_shape_key"
    bl_label = "Convert deformed to a shape key"

    bl_description = "Convert the current status of the mesh into a shape key"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')

    def execute(self, context):

        active = bpy.context.active_object
        if not active.type == "MESH":
            return{"CANCELLED"}
        deformed = SoftDeformedHandler(active)
        deformed.bake_to_shape_key("Captured")

        return {'FINISHED'}

class OT_activate_opposite_weight(bpy.types.Operator):

    bl_idname = "object.activate_mirror_weight"
    bl_label = "Pick the soft Mod opposite weight"

    bl_description = "Pick the soft Mod opposite weight"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'WEIGHT_PAINT')

    def execute(self, context):
        active = bpy.context.active_object
        active_group = active.vertex_groups.active
        active_group_name = active_group.name

        if "_mirror" in active_group_name:
            mirror_group = active_group_name.replace("_mirror", "")
        else:
            mirror_group = str(active_group_name).replace("_deform", "_mirror_deform")

        v_group = active.vertex_groups.get(mirror_group)
        if v_group:
            active.vertex_groups.active_index = v_group.index


        return {'FINISHED'}

class OT_smooth_weight(bpy.types.Operator):
    """ Override delete action
    """
    bl_idname = "object.softmod_smooth"
    bl_label = "Smooth soft mod"

    bl_description = "Alt+Click to smooth the mirror group. \nCtrl+Alt+Click to smooth both."


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode in {'OBJECT', "WEIGHT_PAINT"})



    def invoke(self , context , event):

        if event.alt:
            self.smooth_weights(context, mirror= True)
            if event.ctrl:
                self.smooth_weights (context , mirror=False)

        else:
            self.smooth_weights (context , mirror=False)


        return {'FINISHED'}

    def smooth_weights (self, context, mirror =False):

        if context.active_object.mode == "OBJECT":
            selection = bpy.context.selected_objects
            for selected in selection:

                widget = SoftWidgetHandler.from_widget (selected)
                if widget:
                    widget.smooth_weights(mirror = mirror)

        #if context.active_object.mode == "WEIGHT_GPENCIL":
           # bpy.ops.gpencil.vertex_group_smooth ()
        if context.active_object.mode == "WEIGHT_PAINT":

            active = context.active_object
            active_handler = SoftDeformedHandler (active)

            active_group = active.vertex_groups.active

            if mirror:
                active_handler.smooth_opposite_weight (active_group)
            else:
                active_handler.smooth_weights (active_group.name)

        return {'FINISHED'}





class OT_smooth_paint_weight(bpy.types.Operator):

    bl_idname = "object.smooth_paint_weight"
    bl_label = "Smooth painted vertex group"
    bl_description = "Alt+Click to smooth current and opposite vertex Group."


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'WEIGHT_PAINT')

    def invoke(self , context , event):

        if event.alt:
            self.smooth_weights(context, mirror= True)
            if event.ctrl:
                self.smooth_weights (context , mirror=False)

        else:
            self.smooth_weights (context , mirror=False)


        return {'FINISHED'}


    def smooth_weights(self, context, mirror=False):

        active = context.active_object
        active_handler = SoftDeformedHandler(active)

        active_group = active.vertex_groups.active
        active_handler.smooth_weights(active_group.name)
        if mirror:
            active_handler.smooth_opposite_weight(active_group)


class OT_invert_paint_weight(bpy.types.Operator):

    bl_idname = "object.invert_weight_value"
    bl_label = "Smooth painted vertex group"
    bl_description = "Alt+Click to smooth current and opposite vertex Group."


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'WEIGHT_PAINT')


    def execute(self, context):
        print("I am doing something")
        w = context.scene.tool_settings.unified_paint_settings.weight
        context.scene.tool_settings.unified_paint_settings.weight = 1.0 - w
        return {'FINISHED'}


class OT_mirror_to_opposite_weight(bpy.types.Operator):

    bl_idname = "object.mirror_paint_weight"
    bl_label = "Mirror weights to the opposite group"

    bl_description = "Pick the soft Mod opposite weight"


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'WEIGHT_PAINT')

    def execute(self, context):
        active = bpy.context.active_object
        active_group = active.vertex_groups.active
        handler = SoftDeformedHandler(active)
        handler.mirror_vertex_group(active_group, topology=active.soft_widget.topologycal_sym)
        active.vertex_groups.active_index = active_group.index

        return {'FINISHED'}







class OT_mirror_weights(bpy.types.Operator):

    bl_idname = "object.mirror_soft_weights"
    bl_label = "Mirror weights of the Soft Mod"

    bl_description = "Alt+Click to mirror the opposite side."


    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
            and context.active_object.mode == 'OBJECT')


    def invoke(self , context , event):

        if event.alt:
            self.mirror_weights(context, mirror= True)


        else:
            self.mirror_weights (context , mirror=False)


        return{"FINISHED"}


    def mirror_weights(self, context, mirror):
        active = bpy.context.active_object
        widget = SoftWidgetHandler.from_widget (active)
        widget.mirror_weights(mirror)

