bl_info = {
    "name" : "SoftMod",
    "author" : "Maurizio Memoli",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (2, 1, 0,),
    "location" : "",
    "warning" : "",
    "wiki_url": "",
    "category" : "3D View"
}
import bpy
from . ui.softMod_panel import SoftMod_PT_Panel
from bpy.types import (PropertyGroup)
from bpy.props import (BoolProperty, PointerProperty)
#from . operators.softMod_ops import Create_SoftMod_Operator
from . operators.create_softMod_op import OT_Create_SoftMod_operator
from . operators.ops import OT_delete_override, OT_paint_mode, OT_toggle_soft_mod, OT_smooth_weight,\
    OT_parent_widget,OT_unparent_widget, OT_rename_softMod, OT_convert_to_shape_key, OT_deformed_to_shape_key,\
    OT_mirror_weights, OT_activate_opposite_weight, OT_mirror_to_opposite_weight, OT_smooth_paint_weight, OT_invert_paint_weight



addon_keymaps = []

class SoftWidgetSttings(PropertyGroup):
    topologycal_sym: bpy.props.BoolProperty (default=False)

    widget_relative_size: bpy.props.FloatProperty (default=0.0)


class SoftModSettings(PropertyGroup):
    surf_falloff: BoolProperty(
        name="Surface Falloff",
        description ="Enable surface falloff",
        default=False)

    show_widget_properties: bpy.props.BoolProperty (default=True)

    show_mesh_properties: bpy.props.BoolProperty (default=True)

    show_global_properties: bpy.props.BoolProperty (default=True)

    widget_name: bpy.props.StringProperty (default="")

    widget_global_size: bpy.props.FloatProperty (default=0.0)

    smooth_iterations: bpy.props.IntProperty (default=2, min=0)

    smooth_factor: bpy.props.FloatProperty (default=1.0, min=0.0, max=1.0)

    smooth_expand: bpy.props.FloatProperty (default=0.0, min = 0.0, max= 1.0)




classes = (SoftMod_PT_Panel, OT_Create_SoftMod_operator, OT_delete_override, OT_paint_mode, SoftModSettings,
           OT_toggle_soft_mod, OT_smooth_weight, OT_parent_widget,SoftWidgetSttings,OT_activate_opposite_weight,
           OT_unparent_widget, OT_rename_softMod, OT_convert_to_shape_key, OT_deformed_to_shape_key,
           OT_smooth_paint_weight, OT_mirror_to_opposite_weight, OT_mirror_weights, OT_invert_paint_weight)
#register, unregister = bpy.utils.register_classes_factory(classes)

def register():
    global classes
    global addon_keymaps
    for cl in classes:
        bpy.utils.register_class(cl)

    bpy.types.Scene.soft_mod = PointerProperty (type=SoftModSettings)

    bpy.types.Object.soft_widget = PointerProperty (type=SoftWidgetSttings)

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new("object.create_softmod_op", 'R', 'PRESS', shift=True, ctrl=True)

        addon_keymaps.append ((km , kmi))

        #dkm = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        dkmi = km.keymap_items.new("object.delete_custom", 'DEL', 'PRESS', shift=False, ctrl=True)

        addon_keymaps.append ((km , dkmi))

        #pmkm = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        pmkmi = km.keymap_items.new("object.softmod_paint", 'P', 'PRESS', shift=True, ctrl=True)

        addon_keymaps.append ((km , pmkmi))

        #twkm = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')

        twkmi = km.keymap_items.new("object.softmod_toggle", 'D', 'PRESS', ctrl=True, shift=True)

        addon_keymaps.append ((km , twkmi))


        #xmkm = kcfg.keymaps.new(name='Weight Paint', space_type='WEIGHT_PAINT')
        xmkmi = km.keymap_items.new("object.invert_weight_value" , 'X' , 'PRESS',)

        addon_keymaps.append ((km , xmkmi))


def unregister():
    global classes
    global addon_keymaps


    for cl in classes:
        print(cl)
        bpy.utils.unregister_class(cl)


    for km, kmi in addon_keymaps:
        print(km,kmi)
        km.keymap_items.remove(kmi)


    addon_keymaps.clear()

    del bpy.types.Scene.soft_mod
    del bpy.types.Object.soft_widget
    #del bpy.types.Scene.show_widget_properties

    #del bpy.types.Object.widget_name
    # replace_shortkey (OT_delete_override.bl_idname, "object.delete")
if __name__ == "__main__":
    register()


