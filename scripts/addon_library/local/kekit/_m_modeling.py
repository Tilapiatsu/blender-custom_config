import bpy
import bmesh
from math import sqrt
from bpy.types import Panel, Operator
from . import ke_solo_cutter, ke_merge_to_mouse, ke_ground, ke_merge_near_selected, ke_unbevel, ke_zeroscale, \
    ke_quickscale, ke_fit2grid, ke_collision, ke_nice_project
from ._prefs import pcoll


#
# MODULE UI
#
class UIModelingModule(Panel):
    bl_idname = "UI_PT_M_MODELING"
    bl_label = "Modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = __package__
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator('view3d.ke_solo_cutter').mode = "ALL"
        row.operator('view3d.ke_solo_cutter', text="Solo PreC").mode = "PRE"
        col.operator('object.ke_showcuttermod')

        row = col.row(align=True)
        row.operator('view3d.ke_shading_toggle', text="Flat/Smooth Toggle")
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.prop(k, "shading_tris", text="T", toggle=True)

        col.operator('mesh.merge_to_mouse', icon="MOUSE_MOVE")
        col.operator('mesh.ke_merge_to_active')
        col.operator('mesh.ke_merge_near_selected')

        col.operator('view3d.ke_ground', text="Ground or Center")

        row = col.row(align=True)
        row.operator('mesh.ke_unbevel')
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        if k.unbevel_autoring:
            row2.prop(k, "unbevel_autoring", text="", toggle=True, icon="CHECKMARK")
        else:
            row2.prop(k, "unbevel_autoring", text="", toggle=True, icon_value=pcoll['kekit']['ke_uncheck'].icon_id)

        row = col.row(align=True)
        row.operator('view3d.ke_collision', text="BBox").col_type = "BOX"
        row.operator('view3d.ke_collision', text="Convex Hull").col_type = "CONVEX"

        col.operator('view3d.ke_fit2grid')
        col.operator('mesh.ke_zeroscale', text="ZeroScale to Cursor").orient_type = "CURSOR"
        col.operator('mesh.ke_facematch')

        row = col.row(align=True)
        row.scale_x = 0.85
        row.prop(k, "qs_user_value", text="QScale")
        row.scale_x = 0.15
        row.prop(k, "qs_unit_size", text="U", toggle=True)
        qsx = row.operator('view3d.ke_quickscale', text="X")
        qsy = row.operator('view3d.ke_quickscale', text="Y")
        qsz = row.operator('view3d.ke_quickscale', text="Z")
        qsx.user_axis = "0"
        qsy.user_axis = "1"
        qsz.user_axis = "2"
        qsx.unit_size = k.qs_unit_size
        qsy.unit_size = k.qs_unit_size
        qsz.unit_size = k.qs_unit_size
        qsx.user_value = k.qs_user_value
        qsy.user_value = k.qs_user_value
        qsz.user_value = k.qs_user_value

        col.operator('view3d.ke_nice_project')


#
# MODULE OPERATORS (MISC)
#
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
        tri_mode = context.preferences.addons[__package__].preferences.shading_tris

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


class KeFaceMatch(Operator):
    bl_idname = "mesh.ke_facematch"
    bl_label = "Scale From Face"
    bl_description = "Scales selected object(s) by the size(area) difference of selected faces to match last selected" \
                     "face\nSelect 1 Face per Object, in Multi-Edit mode\nScale will be auto-applied"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH' and
                context.object.data.is_editmode)

    def execute(self, context):
        sel_objects = [o for o in context.selected_objects]

        if len(sel_objects) < 2:
            self.report({"INFO"}, "Invalid Selection (2+ Objects required)")
            return {"CANCELLED"}

        src_obj = context.object
        sel_obj = [o for o in sel_objects if o != src_obj]

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        bpy.ops.object.editmode_toggle()

        bma = bmesh.from_edit_mesh(src_obj.data)
        fa = [f for f in bma.faces if f.select]
        if fa:
            fa = fa[-1]
        else:
            self.report({"INFO"}, "Target Object has no selected face?")
            return {"CANCELLED"}

        ratio = 1

        for o in sel_obj:
            bmb = bmesh.from_edit_mesh(o.data)
            fb = [f for f in bmb.faces if f.select]
            if fb:
                fb = fb[-1]
                try:
                    ratio = sqrt(fa.calc_area() / fb.calc_area())
                except ZeroDivisionError:
                    self.report({"INFO"}, "Zero Division Error. Invalid geometry?")

                o.scale *= ratio

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


class KeShowCutterMod(Operator):
    bl_idname = "object.ke_showcuttermod"
    bl_label = "Show Cutter Modifier"
    bl_description = "Sets object using cutter (in boolean modifier) as active +\n" \
                     "Shows the modifier panel & sets the boolean Modifier as active.\n" \
                     "If many objects use the cutter: run again to cycle objects."
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
            # Show the modifier in the properties tab (and expand)
            context.view_layer.objects.active = obj_to_select
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


#
# MODULE REGISTRATION
#
classes = (
    UIModelingModule,
    KeShadingToggle,
    KeFaceMatch,
    KeShowCutterMod,
)

modules = (
    ke_solo_cutter,
    ke_merge_to_mouse,
    ke_merge_near_selected,
    ke_ground,
    ke_unbevel,
    ke_zeroscale,
    ke_quickscale,
    ke_fit2grid,
    ke_collision,
    ke_nice_project,
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_modeling:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()


def unregister():

    if "bl_rna" in UIModelingModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
