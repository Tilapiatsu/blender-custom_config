
if "bpy" in locals():
    import importlib
    importlib.reload(blend)
    importlib.reload(version)
    importlib.reload(connection)
    importlib.reload(utils)
    importlib.reload(operator)
    importlib.reload(operator_islands)
    importlib.reload(operator_box)
    importlib.reload(prefs)
    importlib.reload(enums)
    importlib.reload(labels)
    importlib.reload(panel)
    importlib.reload(panel_base)
    importlib.reload(pack_context)
    importlib.reload(presets)

bl_info = {
    "name": "UVPackmaster2",
    "author": "glukoz",
    "version": (2, 2, 7),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UV"}


inside_blender = True

try:
    import bpy
except:
    inside_blender = False


if inside_blender:

    from .operator import *
    from .operator_islands import *
    from .operator_box import *
    from .panel import *
    from .prefs import *
    from .register import *
    from .presets import *

    import bpy
    import mathutils


    classes = (
        UVP2_DeviceDesc,
        UVP2_PackStats,
        UVP2_UL_DeviceList,
        UVP2_Preferences,

        UVP2_OT_SelectUvpEngine,
        
        UVP2_OT_PackOperator,
        UVP2_OT_MeasureAreaOperator,
        UVP2_OT_OverlapCheckOperator,
        UVP2_OT_ValidateOperator,
        UVP2_OT_SelectSimilarOperator,
        UVP2_OT_AlignSimilarOperator,
        UVP2_OT_AdjustIslandsToTexture,
        UVP2_OT_UndoIslandsAdjustemntToTexture,

        UVP2_OT_UvpSetupHelp,
        UVP2_OT_NonSquarePackingHelp,
        UVP2_OT_SimilarityDetectionHelp,
        UVP2_OT_InvalidTopologyHelp,
        UVP2_OT_PixelMarginHelp,
        UVP2_OT_IslandRotStepHelp,

        UVP2_OT_ShowRotStepIslandParam,
        UVP2_OT_SetRotStepIslandParam,
        UVP2_OT_ResetRotStepIslandParam,

        UVP2_OT_EnableTargetBox,
        UVP2_OT_DisableTargetBox,
        UVP2_OT_DrawTargetBox,
        UVP2_OT_SetTargetBoxTile,

        UVP2_OT_SavePreset,
        UVP2_OT_LoadPreset,
        UVP2_OT_LoadTargetBox,

        UVP2_PT_Main,
        UVP2_PT_PackingDevice,
        UVP2_PT_BasicOptions,
        UVP2_PT_AdvancedOptions,
        UVP2_PT_Heuristic,
        UVP2_PT_NonSquarePacking,
        UVP2_PT_TargetBox,
        UVP2_PT_IslandRotStep,
        UVP2_PT_Warnings,
        UVP2_PT_Statistics,
        UVP2_PT_Help
    )


    def register():

        handle_annotations(UVP2_DeviceDesc)
        handle_annotations(UVP2_PackStats)
        handle_annotations(UVP2_SceneProps)

        UVP2_Preferences.dev_array = bpy.props.CollectionProperty(type=UVP2_DeviceDesc)
        UVP2_Preferences.stats_array = bpy.props.CollectionProperty(type=UVP2_PackStats)

        bpy.utils.register_class(UVP2_SceneProps)
        bpy.types.Scene.uvp2_props = bpy.props.PointerProperty(type=UVP2_SceneProps)

        for cls in classes:
            handle_annotations(cls)
            bpy.utils.register_class(cls)

        register_specific(bl_info)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

        del bpy.types.Scene.uvp2_props
        bpy.utils.unregister_class(UVP2_SceneProps)

        del UVP2_Preferences.stats_array
        del UVP2_Preferences.dev_array
