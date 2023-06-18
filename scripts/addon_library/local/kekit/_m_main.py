import bpy
from bpy.types import Panel, Operator
from ._utils import get_distance
from . import ke_get_set_edit_mesh, ke_quickmeasure
from ._prefs import pcoll
from math import pi


#
# MODULE UI
#
class UIMainModule(Panel):
    bl_idname = "UI_PT_M_MAIN"
    bl_label = "Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_category = __package__
    bl_parent_id = "UI_PT_kekit"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        k = context.preferences.addons[__package__].preferences
        u = pcoll['kekit']['ke_uncheck'].icon_id

        layout = self.layout
        col = layout.column(align=True)
        hrow = col.row(align=True)
        hrow.scale_y = 0.25
        hrow.enabled = False
        hrow.label(text="Main")
        col.separator(factor=0.5)
        row = col.row(align=True)
        row.operator('view3d.ke_get_set_editmesh', icon="MOUSE_MOVE", text="Get&SetEdit")
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.operator('view3d.ke_get_set_editmesh', text="GSExt").extend = True
        if k.getset_ep:
            row2.prop(k, "getset_ep", text="", toggle=True, icon="CHECKMARK")
        else:
            row2.prop(k, "getset_ep", text="", toggle=True, icon_value=u)
        col.operator('view3d.ke_get_set_material', icon="MOUSE_MOVE", text="Get&Set Material")

        col.operator('object.ke_local_by_distance')
        col.operator('view3d.ke_zerolocal')
        col.operator('view3d.ke_unhide_or_local', icon="HIDE_OFF")

        row = col.row(align=True)
        row.operator('view3d.ke_quickmeasure', icon="DRIVER_DISTANCE", text="QuickMeasure").qm_start = "DEFAULT"
        row2 = row.row(align=True)
        row2.alignment = "RIGHT"
        row2.operator('view3d.ke_quickmeasure', text="QMF").qm_start = "SEL_SAVE"


#
# MODULE OPERATORS (MISC)
#
class KeLocalByDistance(Operator):
    bl_idname = "object.ke_local_by_distance"
    bl_label = "Local Mode by Distance"
    bl_description = "Include objects in Local Mode by distance to selected object"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", min=0, max=9999, default=4.0)
    type: bpy.props.BoolProperty(name="Same Type Only", default=False)
    invert: bpy.props.BoolProperty(name="Invert Range", default=False)
    frame: bpy.props.BoolProperty(name="Frame View", default=False)

    def execute(self, context):
        if context.space_data.local_view:
            bpy.ops.view3d.localview()
        sel_obj = context.object
        objects = context.scene.objects
        reselect = [o for o in context.selected_objects]
        if self.type:
            objects = [i for i in objects if i.type == sel_obj.type]
        selected = []
        for o in objects:
            d = get_distance(sel_obj.location, o.location)
            if self.invert:
                if d >= self.distance:
                    o.select_set(True)
                    selected.append(o)
            else:
                if d <= self.distance:
                    o.select_set(True)
                    selected.append(o)
        bpy.ops.view3d.localview(frame_selected=self.frame)
        for o in selected:
            o.select_set(False)
        for o in reselect:
            o.select_set(True)
        return {"FINISHED"}


class KeUnhideOrLocal(Operator):
    bl_idname = "view3d.ke_unhide_or_local"
    bl_label = "Unhide or Local Off"
    bl_description = "Unhides hidden items OR toggles Local mode OFF, if currently in Local mode" \
                     "\n(Compatible with Zero Local)"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def execute(self, context):
        # fallback for deleting visible context object when hidden objects in scene
        if not context.object:
            hidden = []
            for o in context.scene.objects:
                if o.hide_viewport:
                    hidden.append(o)
            if hidden:
                for o in hidden:
                    o.select_set(True)

        if context.space_data.local_view:
            if "ZeroLocal" in context.object.keys():
                bpy.ops.view3d.ke_zerolocal()
            else:
                bpy.ops.view3d.localview(frame_selected=False)
        else:
            bpy.ops.object.hide_view_clear(select=False)
        return {"FINISHED"}


class KeZeroLocal(Operator):
    bl_idname = "view3d.ke_zerolocal"
    bl_label = "Zero Local"
    bl_description = "Temporarily stores & zeroes Loc+Rot & sets Local View. " \
                     "\nRun ZeroLocal again to exit Local View & restore rotation" \
                     "\n+If no rot/loc -> just Local View"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D" and context.object

    def execute(self, context):
        obj = context.object
        in_local_view = bool(context.space_data.local_view)
        stored_rot = True if "ZeroLocalRot" in obj.keys() else False
        stored_loc = True if "ZeroLocalLoc" in obj.keys() else False

        if not in_local_view and any((stored_loc, stored_rot)):
            self.report({"INFO"}, "Not in Local View but has stored values: Copy/Remove manually (Custom Prop)")
            print("Zero Local: Likely exited Local View without using Zero Local"
                  "\nValues can be found in Object Properties / Custom Properties\nfor manual restoration/removal")
            return {"CANCELLED"}

        if not in_local_view:
            # Store Rotation
            rads = obj.rotation_euler
            pos = obj.location
            if sum(rads) != 0:
                # Store degs for easier manual fix (just copy-paste to rot) should something go wrong...
                degs = (rads[0] * 180 / pi, rads[1] * 180 / pi, rads[2] * 180 / pi)
                obj['ZeroLocalRot'] = degs
                obj.rotation_euler = (0, 0, 0)
            if sum(pos) != 0:
                obj['ZeroLocalLoc'] = pos
                obj.location = (0, 0, 0)

        elif in_local_view:
            if stored_rot:
                # Restore Rotation
                rads = obj['ZeroLocalRot']
                re_rads = (rads[0] * pi / 180, rads[1] * pi / 180, rads[2] * pi / 180)
                obj.rotation_euler = re_rads
                del obj['ZeroLocalRot']
            if stored_loc:
                obj.location = obj['ZeroLocalLoc']
                del obj['ZeroLocalLoc']

        bpy.ops.view3d.localview(frame_selected=False)

        return {"FINISHED"}


#
# MODULE REGISTRATION
#
classes = (
    UIMainModule,
    KeLocalByDistance,
    KeUnhideOrLocal,
    KeZeroLocal
)

modules = (
    ke_quickmeasure,
    ke_get_set_edit_mesh,
)


def register():
    if bpy.context.preferences.addons[__package__].preferences.m_main:
        for c in classes:
            bpy.utils.register_class(c)
        
        for m in modules:
            m.register()


def unregister():
    if "bl_rna" in UIMainModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        for m in modules:
            m.unregister()


if __name__ == "__main__":
    register()
