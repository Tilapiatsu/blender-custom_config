# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


if "bpy" in locals():
    import importlib
    importlib.reload(blend)
    importlib.reload(version)
    importlib.reload(connection)
    importlib.reload(utils)
    importlib.reload(operator)
    importlib.reload(operator_islands)
    importlib.reload(operator_box)
    importlib.reload(operator_uv)
    importlib.reload(prefs)
    importlib.reload(enums)
    importlib.reload(labels)
    importlib.reload(panel)
    importlib.reload(panel_base)
    importlib.reload(pack_context)
    importlib.reload(uv_context)
    importlib.reload(presets)
    importlib.reload(island_params)

bl_info = {
    "name": "UVPackmaster2",
    "author": "glukoz",
    "version": (2, 5, 8),
    "blender": (2, 93, 0),
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
    from .operator_uv import *
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
        UVP2_OT_SelectSimilar,
        UVP2_OT_AlignSimilar,
        UVP2_OT_AdjustIslandsToTexture,
        UVP2_OT_UndoIslandsAdjustemntToTexture,

        UVP2_OT_UvpSetupHelp,
        UVP2_OT_HeuristicSearchHelp,
        UVP2_OT_NonSquarePackingHelp,
        UVP2_OT_SimilarityDetectionHelp,
        UVP2_OT_InvalidTopologyHelp,
        UVP2_OT_PixelMarginHelp,
        UVP2_OT_IslandRotStepHelp,
        UVP2_OT_UdimSupportHelp,
        UVP2_OT_ManualGroupingHelp,

        UVP2_OT_ShowRotStepIslandParam,
        UVP2_OT_SetRotStepIslandParam,
        UVP2_OT_ResetRotStepIslandParam,

        UVP2_OT_ShowManualGroupIslandParam,
        UVP2_OT_SetManualGroupIslandParam,
        UVP2_OT_ResetManualGroupIslandParam,
        UVP2_OT_SelectManualGroupIslandParam,

        UVP2_OT_ShowLockGroupIslandParam,
        UVP2_OT_SetLockGroupIslandParam,
        UVP2_OT_SetFreeLockGroupIslandParam,
        UVP2_OT_ResetLockGroupIslandParam,
        UVP2_OT_SelectLockGroupIslandParam,
        UVP2_OT_SelectNonDefaultLockGroupIslandParam,

        UVP2_OT_EnableTargetBox,
        UVP2_OT_DisableTargetBox,
        UVP2_OT_DrawTargetBox,
        UVP2_OT_SetTargetBoxTile,
        UVP2_OT_MoveTargetBoxTile,

        UVP2_OT_SavePreset,
        UVP2_OT_LoadPreset,
        UVP2_OT_LoadTargetBox,
        UVP2_OT_ResetToDefaults,

        UVP2_OT_SplitOverlappingIslands,
        UVP2_OT_UndoIslandSplit,
        UVP2_OT_AdjustScaleToUnselected,
        UVP2_OT_DebugIslands,
        UVP2_OT_SelectIslandsInsideTargetBox,

        UVP2_OT_SetRotStep,
        UVP2_MT_SetRotStep,

        UVP2_PT_Main,
        UVP2_PT_PackingDevice,
        UVP2_PT_BasicOptions,
        UVP2_PT_AdvancedOptions,
        UVP2_PT_PixelMargin,
        UVP2_PT_Heuristic,
        UVP2_PT_NonSquarePacking,
        UVP2_PT_TargetBox,
        UVP2_PT_IslandRotStep,
        UVP2_PT_ManualGrouping,
        UVP2_PT_LockGroups,
        UVP2_PT_Hints,
        UVP2_PT_Statistics,
        UVP2_PT_Help
    )


    def register():

        bpy.utils.register_class(UVP2_SceneProps)
        bpy.types.Scene.uvp2_props = bpy.props.PointerProperty(type=UVP2_SceneProps)

        for cls in classes:
            bpy.utils.register_class(cls)

        register_specific(bl_info)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

        del bpy.types.Scene.uvp2_props
        bpy.utils.unregister_class(UVP2_SceneProps)
