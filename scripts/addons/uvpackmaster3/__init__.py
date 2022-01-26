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
from . import module_loader
module_loader.unload_uvpm3_modules(locals())

bl_info = {
    "name": "UVPackmaster3",
    "author": "glukoz",
    "version": (3, 0, 4),
    "blender": (3, 0, 0),
    "location": "",
    "description": "",
    "warning": "",
    "doc_url": "",
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
    from .register_utils import *
    from .presets import *
    from .presets_grouping_scheme import *
    from .mode import *
    from .grouping import *
    from .grouping_scheme import *
    from .grouping_scheme_ui import *

    import bpy
    import mathutils

    from .scripted_pipeline import panels
    scripted_panels_modules = module_loader.import_submodules(panels)
    scripted_panels_classes = module_loader.get_registrable_classes(scripted_panels_modules, sub_class=UVPM3_PT_Registerable)
    scripted_panels_classes.sort(key=lambda x: x.PANEL_PRIORITY)

    from .scripted_pipeline import operators
    scripted_operators_modules = module_loader.import_submodules(operators)
    scripted_operators_classes = module_loader.get_registrable_classes(scripted_operators_modules, sub_class=UVPM3_OT_Generic)

    from .scripted_pipeline import modes
    scripted_modes_modules = module_loader.import_submodules(modes)
    scripted_modes_classes = module_loader.get_registrable_classes(scripted_modes_modules,
                                                                   sub_class=UVPM3_Mode_Generic, required_vars=("MODE_ID",))
    scripted_modes_classes.sort(key=lambda x: x.MODE_PRIORITY)


    classes = (
        UVPM3_UL_GroupInfo,
        UVPM3_UL_TargetBoxes,
        UVPM3_MT_BrowseGroupingSchemes,
        UVPM3_OT_BrowseGroupingSchemes,

        UVPM3_Box,
        UVPM3_GroupInfo,
        UVPM3_GroupingOptionsBase,
        UVPM3_GroupingOptions,
        UVPM3_AutoGroupingOptions,
        UVPM3_GroupingScheme,

        # UVPM3_BenchmarkEntry,
        UVPM3_DeviceSettings,
        UVPM3_SavedDeviceSettings,
        # UVPM3_DeviceDesc,
        # UVPM3_UL_DeviceList,
        UVPM3_Preferences,

        UVPM3_MT_BrowseModes,
        UVPM3_OT_SelectMode,

        UVPM3_OT_SetEnginePath,
        UVPM3_OT_AdjustIslandsToTexture,
        UVPM3_OT_UndoIslandsAdjustemntToTexture,

        UVPM3_OT_Help,
        UVPM3_OT_MainModeHelp,
        UVPM3_OT_SetupHelp,

        UVPM3_OT_RotStepShowIParam,
        UVPM3_OT_RotStepSetIParam,
        UVPM3_OT_RotStepResetIParam,

        UVPM3_OT_ScaleLimitShowIParam,
        UVPM3_OT_ScaleLimitSetIParam,
        UVPM3_OT_ScaleLimitResetIParam,

        UVPM3_OT_ShowManualGroupIParam,
        UVPM3_OT_SetManualGroupIParam,
        UVPM3_OT_ResetManualGroupIParam,
        UVPM3_OT_SelectManualGroupIParam,

        UVPM3_OT_ShowLockGroupIParam,
        UVPM3_OT_SetLockGroupIParam,
        UVPM3_OT_SetFreeLockGroupIParam,
        UVPM3_OT_ResetLockGroupIParam,
        UVPM3_OT_SelectLockGroupIParam,
        UVPM3_OT_SelectNonDefaultLockGroupIParam,

        UVPM3_OT_AlignPriorityShowIParam,
        UVPM3_OT_AlignPrioritySetIParam,
        UVPM3_OT_AlignPriorityResetIParam,

        UVPM3_OT_FinishBoxRendering,
        
        # UVPM3_OT_RenderGroupBoxes,
        UVPM3_OT_RenderGroupingSchemeBoxes,
        UVPM3_OT_SetGroupingSchemeBoxToTile,
        UVPM3_OT_MoveGroupingSchemeBox,

        UVPM3_OT_RenderCustomTargetBox,
        UVPM3_OT_SetCustomTargetBoxToTile,
        UVPM3_OT_MoveCustomTargetBox,

        UVPM3_PT_Presets,
        UVPM3_PT_PresetsCustomTargetBox,
        UVPM3_PT_PresetsGroupingScheme,
        UVPM3_OT_SavePreset,
        UVPM3_OT_SaveGroupingSchemePreset,
        UVPM3_OT_RemovePreset,
        UVPM3_OT_LoadPreset,
        UVPM3_OT_LoadTargetBox,
        UVPM3_OT_LoadGroupingSchemePreset,
        UVPM3_OT_ResetToDefaults,

        UVPM3_OT_NewGroupingScheme,
        UVPM3_OT_RemoveGroupingScheme,
        UVPM3_OT_UnlinkGroupingScheme,
        UVPM3_OT_NewGroupInfo,
        UVPM3_OT_RemoveGroupInfo,
        UVPM3_OT_MoveGroupInfo,
        UVPM3_OT_NewTargetBox,
        UVPM3_OT_RemoveTargetBox,
        UVPM3_OT_MoveTargetBox,


        UVPM3_OT_SetRotStep,
        UVPM3_MT_SetRotStep,

        UVPM3_PT_AuxOperations,
        UVPM3_PT_Main,

        UVPM3_ScriptedPipelineProperties,
        UVPM3_SceneProps
    )


    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

        for cls in scripted_panels_classes:
            bpy.utils.register_class(cls)

        for cls in scripted_operators_classes:
            bpy.utils.register_class(cls)

        bpy.types.Scene.uvpm3_props = bpy.props.PointerProperty(type=UVPM3_SceneProps)

        register_modes(scripted_modes_classes)
        register_specific(bl_info)

    def unregister():
        for cls in reversed(scripted_operators_classes):
            bpy.utils.unregister_class(cls)

        for cls in reversed(scripted_panels_classes):
            bpy.utils.unregister_class(cls)

        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)

        bpy.utils.unregister_class(UVPM3_PT_EngineStatus)

        del bpy.types.Scene.uvpm3_props
