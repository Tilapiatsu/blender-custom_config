bl_info = {
    "name": "kekit_subd",
    "author": "Kjell Emanuelsson",
    "category": "Modeling",
    "version": (1, 0, 4),
    "blender": (2, 80, 0),
}
import bpy
from bpy.types import Operator


class VIEW3D_OT_ke_subd(Operator):
    bl_idname = "view3d.ke_subd"
    bl_label = "Toggle/Set Subd Levels"
    bl_options = {'REGISTER', 'UNDO'}

    level_mode : bpy.props.EnumProperty(
        items=[("TOGGLE", "Toggle Subd", "", "TOGGLE", 1),
               ("VIEWPORT", "Set Viewport Levels", "", "VIEWPORT", 2),
               ("RENDER", "Set Render Levels", "", "RENDER", 3)
               ],
        name="Level Mode",
        options={'HIDDEN'},
        default="TOGGLE")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        if properties.level_mode == "VIEWPORT":
            return "Set Viewport SubD Level on selected Object(s) (using options value)"
        elif properties.level_mode == "RENDER":
            return "Set Render SubD Level on selected Object(s) (using options value)"
        else:
            return "Toggles (add if none exist) SubD modifier(s) on selected object(s), as defined by options"


    def execute(self, context):

        vp_level = bpy.context.scene.kekit.vp_level
        render_level = bpy.context.scene.kekit.render_level
        flat_edit = bpy.context.scene.kekit.flat_edit
        limit_surface = bpy.context.scene.kekit.limit_surface
        boundary_smooth = bpy.context.scene.kekit.boundary_smooth
        optimal_display = bpy.context.scene.kekit.optimal_display
        on_cage = bpy.context.scene.kekit.on_cage

        mode = context.mode[:]
        if mode == "EDIT_MESH": mode = "EDIT"
        new_subd = []
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        sel_objects = [o for o in context.selected_objects if o.type in cat]
        mode_objects = [o for o in context.objects_in_mode if o.type in cat]
        if not sel_objects and mode_objects:
            sel_objects = mode_objects

        # APPLY NEW SUBSURF IF NONE (TOGGLE)
        if self.level_mode == "TOGGLE":
            subd_objects = []

            for o in sel_objects:
                for mod in o.modifiers:
                    if mod.type == "SUBSURF":
                        subd_objects.append(o)
                        break

            new = [o for o in sel_objects if o not in subd_objects]
            for obj in new:
                mod = obj.modifiers.new(name="Subdivison", type="SUBSURF")

                mod.levels = vp_level
                mod.render_levels = render_level
                mod.boundary_smooth = boundary_smooth
                mod.use_limit_surface = limit_surface
                mod.show_only_control_edges = optimal_display
                mod.show_on_cage = on_cage

                obj.data.use_auto_smooth = False

                if mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.shade_smooth()
                    bpy.ops.object.mode_set(mode=mode)
                else:
                    bpy.ops.object.shade_smooth()
                new_subd.append(obj)

        # MAIN
        for obj in sel_objects:

            if obj not in new_subd:
                set_flat = False
                auto_smooth = False

                for mod in obj.modifiers:

                    if mod.type =="SUBSURF":

                        if self.level_mode == "VIEWPORT":
                            mod.levels = vp_level
                        elif self.level_mode == "RENDER":
                            mod.render_levels = render_level

                        elif self.level_mode == "TOGGLE":

                            if mod.show_viewport:
                                mod.show_viewport = False

                                # re-applying these for otherwise added subd modifiers
                                mod.boundary_smooth = boundary_smooth
                                mod.use_limit_surface = limit_surface
                                mod.show_only_control_edges = optimal_display
                                mod.show_on_cage = on_cage

                                auto_smooth = True
                                if flat_edit:
                                    set_flat = True

                            elif not mod.show_viewport:
                                auto_smooth = False
                                mod.show_viewport = True

                if self.level_mode == "TOGGLE":
                    if auto_smooth:
                        obj.data.use_auto_smooth = True
                    else:
                        obj.data.use_auto_smooth = False

                    if set_flat:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_flat()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_flat()
                    else:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_smooth()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_smooth()

        return {"FINISHED"}


class VIEW3D_OT_ke_subd_step(Operator):
    bl_idname = "view3d.ke_subd_step"
    bl_label = "Step Subd Levels"
    bl_options = {'REGISTER', 'UNDO'}

    step_up : bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        if properties.step_up:
            return "Step-up Viewport SubD Level +1 on selected Object(s)"
        else:
            return "Step-down Viewport SubD Level -1 on selected Object(s)"

    def execute(self, context):
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        sel_objects = [o for o in context.selected_objects if o.type in cat]
        mode_objects = [o for o in context.objects_in_mode if o.type in cat]
        if not sel_objects and mode_objects:
            sel_objects = mode_objects

        if sel_objects:
            for o in sel_objects:
                for mod in o.modifiers:
                    if mod.type == "SUBSURF":
                        if self.step_up:
                            mod.levels += 1
                        else:
                            mod.levels -= 1
        else:
            self.report({"INFO"}, "Invalid Type Selection")
            return {'CANCELLED'}
        return {'FINISHED'}


# -------------------------------------------------------------------------------------------------
# Class Registration & Unregistration
# -------------------------------------------------------------------------------------------------
classes = (
	VIEW3D_OT_ke_subd,
    VIEW3D_OT_ke_subd_step
)

def register():
	for c in classes:
		bpy.utils.register_class(c)

def unregister():
	for c in reversed(classes):
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
