
import bpy

from .panel_base import *

uvp_panel_category = 'UVPackmaster2'
uvp_region_type = 'UI'

class UVP2_PT_Main(UVP2_PT_MainBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_category = uvp_panel_category

class UVP2_PT_PackingDevice(UVP2_PT_PackingDeviceBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_BasicOptions(UVP2_PT_BasicOptionsBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_IslandRotStep(UVP2_PT_IslandRotStepBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_Heuristic(UVP2_PT_HeuristicBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_NonSquarePacking(UVP2_PT_NonSquarePackingBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_AdvancedOptions(UVP2_PT_AdvancedOptionsBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_TargetBox(UVP2_PT_TargetBoxBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_Warnings(UVP2_PT_WarningsBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_Statistics(UVP2_PT_StatisticsBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_Help(UVP2_PT_HelpBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category