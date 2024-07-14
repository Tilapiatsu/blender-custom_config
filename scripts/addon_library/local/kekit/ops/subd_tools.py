import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator, Panel
from .._utils import get_prefs


class UISubDModule(Panel):
    bl_idname = "UI_PT_M_SUBD"
    bl_label = "SubD Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_M_MODIFIERS"

    def draw(self, context):
        k = get_prefs()
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('view3d.ke_subd_step', text="Step VP Lv +1").step_up = True
        row.operator('view3d.ke_subd_step', text="Step VP Lv -1").step_up = False
        row = col.row(align=True)
        row.operator('view3d.ke_subd', text="Set VP Lv").level_mode = "VIEWPORT"
        row.operator('view3d.ke_subd', text="Set Render Lv").level_mode = "RENDER"
        col.separator()
        col = col.box().column(align=True)
        col.operator('view3d.ke_subd', text="SubD Toggle").level_mode = "TOGGLE"
        # col.separator()
        col.label(text="SubD Toggle Options")
        row = col.row(align=True)
        row.prop(k, "vp_level", text="VP Lv")
        row.prop(k, "render_level", text="Render Lv")
        col.separator()
        row = col.row(align=True)
        row.alignment = "LEFT"
        row.label(text="Boundary")
        row.prop(k, "boundary_smooth", text="")
        col.separator(factor=0.5)
        col.prop(k, "limit_surface")
        col.prop(k, "flat_edit", text="Flat Shade when off")
        col.prop(k, "optimal_display")
        col.prop(k, "on_cage")
        col.prop(k, "em_vis")
        col.prop(k, "subd_autosmooth")


class KeSubd(Operator):
    bl_idname = "view3d.ke_subd"
    bl_label = "Toggle/Set Subd Levels"
    bl_options = {'REGISTER', 'UNDO'}

    level_mode: EnumProperty(
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
        k = get_prefs()
        vp_level = k.vp_level
        render_level = k.render_level
        flat_edit = k.flat_edit
        limit_surface = k.limit_surface
        boundary_smooth = k.boundary_smooth
        optimal_display = k.optimal_display
        on_cage = k.on_cage
        em_vis = k.em_vis
        toggle_autosmooth = bool(k.subd_autosmooth)
        if bpy.app.version >= (4, 1):
            toggle_autosmooth = False

        mode = context.mode[:]
        if mode == "EDIT_MESH":
            mode = "EDIT"
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
                mod.show_in_editmode = em_vis

                if toggle_autosmooth:
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

                for mod in obj.modifiers:

                    if mod.type == "SUBSURF":
                        if self.level_mode == "VIEWPORT":
                            mod.levels = vp_level
                        elif self.level_mode == "RENDER":
                            mod.render_levels = render_level

                        elif self.level_mode == "TOGGLE":
                            if mod.show_viewport:
                                # TURN OFF
                                mod.show_viewport = False
                                if toggle_autosmooth:
                                    obj.data.use_auto_smooth = True

                                # re-applying these for subd modifiers added by other means
                                mod.boundary_smooth = boundary_smooth
                                mod.use_limit_surface = limit_surface
                                mod.show_only_control_edges = optimal_display
                                mod.show_on_cage = on_cage
                                mod.show_in_editmode = em_vis

                                if flat_edit:
                                    set_flat = True

                            elif not mod.show_viewport:
                                # TURN ON
                                mod.show_viewport = True
                                if toggle_autosmooth:
                                    obj.data.use_auto_smooth = False

                if self.level_mode == "TOGGLE":
                    if flat_edit and set_flat:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_flat()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_flat()
                    elif flat_edit:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_smooth()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_smooth()

        return {"FINISHED"}


class KeSubDStep(Operator):
    bl_idname = "view3d.ke_subd_step"
    bl_label = "Step Subd Levels"
    bl_options = {'REGISTER', 'UNDO'}

    step_up: BoolProperty(default=True, options={"HIDDEN"})

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
