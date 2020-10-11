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

class UVP2_PT_ManualGrouping(UVP2_PT_ManualGroupingBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_LockGroups(UVP2_PT_LockGroupsBase):
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

class UVP2_PT_PixelMargin(UVP2_PT_PixelMarginBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_TargetBox(UVP2_PT_TargetBoxBase):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = uvp_region_type
    bl_parent_id = UVP2_PT_Main.bl_idname
    bl_category = uvp_panel_category

class UVP2_PT_Hints(UVP2_PT_HintsBase):
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