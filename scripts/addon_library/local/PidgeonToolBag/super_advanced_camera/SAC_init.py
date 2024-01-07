import bpy
import bpy.utils.previews

from . import (
    SAC_Settings,
    SAC_Operators,
    SAC_Panel,
    SAC_List,
    SAC_Functions,
)


def register_function():

    SAC_Settings.register_function()
    SAC_List.register_function()
    SAC_Operators.register_function()
    SAC_Panel.register_function()

    bpy.types.Scene.last_used_id = bpy.props.IntProperty(name="Last Used ID", default=0)
    bpy.types.Scene.sac_effect_list = bpy.props.CollectionProperty(type=SAC_List.SAC_EffectList)
    bpy.types.Scene.sac_effect_list_index = bpy.props.IntProperty(name="Index for sac_effect_list", default=0, update=SAC_Functions.active_effect_update)

    bpy.types.Scene.effect_previews = SAC_Functions.load_effect_previews()
    bpy.types.Scene.bokeh_previews = SAC_Functions.load_bokeh_previews()
    bpy.types.Scene.filter_previews = SAC_Functions.load_filter_previews()
    bpy.types.Scene.gradient_previews = SAC_Functions.load_gradient_previews()


def unregister_function():

    SAC_Panel.unregister_function()
    SAC_Operators.unregister_function()
    SAC_List.unregister_function()
    SAC_Settings.unregister_function()

    del bpy.types.Scene.last_used_id
    del bpy.types.Scene.sac_effect_list
    del bpy.types.Scene.sac_effect_list_index

    bpy.utils.previews.remove(bpy.types.Scene.effect_previews)
    bpy.utils.previews.remove(bpy.types.Scene.bokeh_previews)
    bpy.utils.previews.remove(bpy.types.Scene.filter_previews)
    bpy.utils.previews.remove(bpy.types.Scene.gradient_previews)
