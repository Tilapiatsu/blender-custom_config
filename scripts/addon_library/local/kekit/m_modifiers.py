import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Panel, Operator
from ._ui import pcoll
from ._utils import get_prefs
from .ops.ke_mod_vis import KeToggleModVis
from .ops.ke_shading_toggle import KeShadingToggle
from .ops.ke_showcuttermod import KeShowCutterMod
from .ops.ke_solo_cutter import KeSoloCutter
from .ops.subd_tools import KeSubd, KeSubDStep, UISubDModule


class UIModifiersModule(Panel):
    bl_idname = "UI_PT_M_MODIFIERS"
    bl_label = "Modifiers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "UI_PT_kekit"

    def draw(self, context):
        k = get_prefs()
        u = pcoll['kekit']['ke_uncheck'].icon_id
        c = pcoll['kekit']['ke_check'].icon_id
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator('view3d.ke_solo_cutter').mode = "ALL"
        row.operator('view3d.ke_solo_cutter', text="Solo PreC").mode = "PRE"
        col.operator('object.ke_showcuttermod')
        col.operator('view3d.ke_toggle_mod_vis')

        row = col.row(align=True)
        row.operator('view3d.ke_shading_toggle', text="Flat/Smooth Toggle")
        row.prop(k, "shading_tris", text="", toggle=True, icon_value=c if k.shading_tris else u)

        row = col.row(align=True)
        row.operator('mesh.ke_toggle_weight', text="Toggle Bevel Weight").wtype = "BEVEL"
        row.prop(k, "toggle_same", text="", toggle=True, icon_value=c if k.toggle_same else u)
        row.prop(k, "toggle_add", text="", toggle=True, icon="ADD")

        row = col.row(align=True)
        row.operator('mesh.ke_toggle_weight', text="Toggle Crease Weight").wtype = "CREASE"
        row.prop(k, "toggle_same", text="", toggle=True, icon_value=c if k.toggle_same else u)
        row.prop(k, "toggle_add", text="", toggle=True, icon="ADD")


class KeModOrder(Operator):
    bl_idname = "ke.mod_order"
    bl_description = ("Moves Weighted Normal last in modifier stack (& sets AutoSmooth)\n"
                      "Note: All 'Add Bevel' ops & Toggle Weight automatically run this op")
    bl_label = "Mod Order"
    bl_options = {'INTERNAL'}

    obj_name: StringProperty()
    mod_type: StringProperty()
    top: BoolProperty(default=False)
    obj = None

    def execute(self, context):
        self.obj = bpy.data.objects[self.obj_name]

        if not self.mod_type:
            smods = [m for m in self.obj.modifiers if m.type == "SUBSURF"]
            vnmods = [m for m in self.obj.modifiers if m.type == "WEIGHTED_NORMAL"]
            mods = vnmods + smods
        else:
            mods = [m for m in self.obj.modifiers if m.type == self.mod_type]

        if not mods:
            return {"CANCELLED"}

        for mod in mods:
            # Set as appropriate for general workflow types?
            # if mod.type == "SUBSURF":
            #     self.obj.data.use_auto_smooth = False
            if mod.type == "WEIGHTED_NORMAL":
                self.obj.data.use_auto_smooth = True

            vn_index = self.obj.modifiers.find(mod.name)
            if vn_index != -1:
                with bpy.context.temp_override(**{'object': self.obj}):
                    if self.top:
                        for i in range(vn_index):
                            bpy.ops.object.modifier_move_up(modifier=mod.name)
                    else:
                        for i in range(vn_index, len(self.obj.modifiers) - 1):
                            bpy.ops.object.modifier_move_down(modifier=mod.name)
        return {'FINISHED'}


classes = (
    UIModifiersModule,
    UISubDModule,
    KeSubd,
    KeSubDStep,
    KeSoloCutter,
    KeShowCutterMod,
    KeShadingToggle,
    KeToggleModVis,
    KeModOrder,
)


def register():
    k = get_prefs()
    if k.m_modeling:
        for c in classes:
            bpy.utils.register_class(c)


def unregister():
    if "bl_rna" in UIModifiersModule.__dict__:
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
