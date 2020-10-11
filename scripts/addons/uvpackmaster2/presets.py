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


import os
import json

from .utils import *
from .version import UvpVersionInfo

import bpy
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper
        )


PRESET_PROPERTIES_V1 = [
    'overlap_check',
    'area_measure',
    'precision',
    'margin',
    'pixel_margin',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'postscale_disable',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'group_mode',
    'group_method',
    'tiles_in_row',
    'lock_overlapping',
    'pre_validate',
    'heuristic_enable',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V2 = [
    'overlap_check',
    'area_measure',
    'precision',
    'margin',
    'pixel_margin',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'postscale_disable',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'tiles_in_row',
    'lock_overlapping',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V3 = [
    'overlap_check',
    'area_measure',
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'postscale_disable',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'tiles_in_row',
    'lock_overlapping',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V4 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'manual_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V5 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'manual_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V6 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_method',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'manual_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping_mode',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'heuristic_max_wait_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V7 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_method',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'group_compactness',
    'manual_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping_mode',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'heuristic_max_wait_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V8 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_method',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'normalize_islands',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'group_compactness',
    'manual_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping_mode',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'heuristic_max_wait_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V9 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_method',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'normalize_islands',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'group_compactness',
    'manual_group_num',
    'lock_groups_enable',
    'lock_group_num',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping_mode',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'heuristic_max_wait_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_V10 = [
    'precision',
    'margin',
    'pixel_margin',
    'pixel_padding',
    'pixel_margin_method',
    'pixel_margin_tex_size',
    'rot_enable',
    'prerot_disable',
    'fixed_scale',
    'fixed_scale_strategy',
    'normalize_islands',
    'rot_step',
    'island_rot_step_enable',
    'island_rot_step',
    'tex_ratio',
    'pack_to_others',
    'pack_mode',
    'group_method',
    'group_compactness',
    'manual_group_num',
    'lock_groups_enable',
    'lock_group_num',
    'use_blender_tile_grid',
    'tile_count',
    'tiles_in_row',
    'lock_overlapping_mode',
    'pre_validate',
    'heuristic_enable',
    'heuristic_search_time',
    'heuristic_max_wait_time',
    'pixel_margin_adjust_time',
    'advanced_heuristic',
    'similarity_threshold',
    'multi_device_pack',
    'fully_inside',
    'move_islands',
    'target_box_tile_x',
    'target_box_tile_y',
    'target_box_p1_x',
    'target_box_p1_y',
    'target_box_p2_x',
    'target_box_p2_y'
]

PRESET_PROPERTIES_LATEST = PRESET_PROPERTIES_V10


class UVP2_OT_SavePreset(bpy.types.Operator, ExportHelper):

    bl_idname = 'uvpackmaster2.save_preset'
    bl_label = 'Save Preset'
    bl_description = 'Save all packer options to a file'

    filename_ext = ".uvpp"
    filter_glob = bpy.props.StringProperty(
        default="*.uvpp",
        options={'HIDDEN'},
        )
    
    def execute(self, context):

        try:

            prefs = get_prefs()

            scene_props = context.scene.uvp2_props
            props_dict = {}

            for prop_name in PRESET_PROPERTIES_LATEST:
                props_dict[prop_name] = getattr(scene_props, prop_name)

            json_struct = {
                'version_major': UvpVersionInfo.ADDON_VERSION_MAJOR,
                'version_minor': UvpVersionInfo.ADDON_VERSION_MINOR,
                'version_patch': UvpVersionInfo.ADDON_VERSION_PATCH,
                'properties' : props_dict
            }

            json_str = json.dumps(json_struct)
            
            with open (self.filepath, "w") as file:
                file.write(json_str)
                
            self.report({'INFO'}, 'Preset saved')

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')

        return {'FINISHED'}
    
    def draw(self, context):
        pass

    def post_op(self):
        pass
       

class UVP2_OT_LoadPresetBase(bpy.types.Operator):

    filename_ext = ".uvpp"
    filter_glob = bpy.props.StringProperty(
        default="*.uvpp",
        options={'HIDDEN'},
        )

    def raise_invalid_format(self):
        raise RuntimeError('Invalid format')

    def addon_to_preset_version(self, addon_version):

        if addon_version == (2,2,0):
            return 1

        if addon_version in {(2,2,5), (2,2,6)}:
            return 2

        if addon_version == (2,2,7):
            return 3

        if addon_version in {(2,3,0), (2,3,1)}:
            return 4

        if addon_version == (2,3,2):
            return 5

        if addon_version == (2,3,5):
            return 6

        if addon_version in {(2,4,0), (2,4,2), (2,4,3)}:
            return 7

        if addon_version == (2,4,4):
            return 8

        if addon_version == (2,4,5):
            return 9

        if addon_version == (2,5,0):
            return 10

        raise RuntimeError('Unsupported preset version')

    def translate_props_1to2(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V1:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        group_mode = props_dict['group_mode']
        del props_dict['group_mode']

        if group_mode == UvGroupingMode_Legacy.PACK_TOGETHER.code:
            pack_mode = UvPackingMode.GROUPS_TOGETHER.code
        elif group_mode == UvGroupingMode_Legacy.PACK_TO_TILES.code:
            pack_mode = UvPackingMode.GROUPS_TO_TILES.code
        else:
            pack_mode = UvPackingMode.SINGLE_TILE.code

        props_dict['pack_mode'] = pack_mode
        props_dict['heuristic_search_time'] = 0

    def translate_props_2to3(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V2:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['pixel_padding'] = 0

    def translate_props_3to4(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V3:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        del props_dict['overlap_check']
        del props_dict['area_measure']
        del props_dict['postscale_disable']

        props_dict['fixed_scale'] = False
        props_dict['manual_group_num'] = 0
        props_dict['tile_count'] = 2

    def translate_props_4to5(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V4:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['fully_inside'] = True
        props_dict['move_islands'] = False

    def translate_props_5to6(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V5:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['pixel_margin_method'] = UvPixelMarginMethod.ADJUSTMENT_TIME.code
        props_dict['heuristic_max_wait_time'] = 0
        props_dict['lock_overlapping_mode'] = UvLockOverlappingMode.ANY_PART.code if props_dict['lock_overlapping'] else UvLockOverlappingMode.DISABLED.code
        del props_dict['lock_overlapping']

    def translate_props_6to7(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V6:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['group_compactness'] = 0.0

    def translate_props_7to8(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V7:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['normalize_islands'] = False

    def translate_props_8to9(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V8:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['lock_groups_enable'] = False
        props_dict['lock_group_num'] = 1

    def translate_props_9to10(self, props_dict):

        for prop_name in PRESET_PROPERTIES_V9:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        props_dict['fixed_scale_strategy'] = UvFixedScaleStrategy.BOTTOM_TOP.code
        props_dict['use_blender_tile_grid'] = False

    def translate_props(self, preset_version, props_dict):

        translate_array = [
            self.translate_props_1to2,
            self.translate_props_2to3,
            self.translate_props_3to4,
            self.translate_props_4to5,
            self.translate_props_5to6,
            self.translate_props_6to7,
            self.translate_props_7to8,
            self.translate_props_8to9,
            self.translate_props_9to10 ]

        for i in range(preset_version-1, len(translate_array)):
            translate_array[i](props_dict)

    def read_preset(self):

        with open (os.path.join(self.filepath), "r") as file:
            json_str = file.read()
            
        try:
            json_struct = json.loads(json_str)
        except:
            self.raise_invalid_format()

        if type(json_struct) is not dict:
            self.raise_invalid_format()

        try:
            addon_version_saved = (json_struct['version_major'], json_struct['version_minor'], json_struct['version_patch'])
            props_dict = json_struct['properties']
        except:
            self.raise_invalid_format()

        preset_version = self.addon_to_preset_version(addon_version_saved)
        self.translate_props(preset_version, props_dict)

        for prop_name in PRESET_PROPERTIES_LATEST:
            if prop_name not in props_dict:
                self.raise_invalid_format()

        return props_dict

    def execute(self, context):

        try:
            props_dict = self.read_preset()

            prefs = get_prefs()
            scene_props = context.scene.uvp2_props   

            for prop_name in self.props_to_load:
                setattr(scene_props, prop_name, props_dict[prop_name])
                
            self.post_op()
            redraw_ui(context)
            
            self.report({'INFO'}, self.success_msg)

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))

        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')

        return {'FINISHED'}

    def post_op(self):
        pass
    
    def draw(self, context):
        pass


class UVP2_OT_LoadPreset(UVP2_OT_LoadPresetBase, ImportHelper):

    filename_ext = UVP2_OT_LoadPresetBase.filename_ext
    filter_glob = UVP2_OT_LoadPresetBase.filter_glob

    bl_idname = 'uvpackmaster2.load_preset'
    bl_label = 'Open Preset'
    bl_options = {'UNDO'}
    bl_description = 'Load all packer options from a file'

    props_to_load = PRESET_PROPERTIES_LATEST
    success_msg = 'Preset loaded'


class UVP2_OT_LoadTargetBox(UVP2_OT_LoadPresetBase, ImportHelper):

    filename_ext = UVP2_OT_LoadPresetBase.filename_ext
    filter_glob = UVP2_OT_LoadPresetBase.filter_glob

    bl_idname = 'uvpackmaster2.load_target_box'
    bl_label = 'Load Box From Preset'
    bl_options = {'UNDO'}
    bl_description = 'Load the packing box coordinates from a preset file'

    props_to_load = [
        'target_box_p1_x',
        'target_box_p1_y',
        'target_box_p2_x',
        'target_box_p2_y'
    ]
    success_msg = 'Box loaded'


    def post_op(self):
        
        if is_blender28():
            bpy.ops.uvpackmaster2.enable_target_box()


class UVP2_OT_ResetToDefaults(bpy.types.Operator):

    bl_idname = 'uvpackmaster2.reset_to_defaults'
    bl_label = 'Reset To Defaults'
    bl_description = 'Reset all UVP parameters to default values'

    CONFIRMATION_MSG = 'Are you sure you want to reset all UVP parameters to default values?'
    
    def execute(self, context):

        for prop_name in PRESET_PROPERTIES_LATEST:
            context.scene.uvp2_props.property_unset(prop_name)

        prefs = get_prefs()
        prefs.property_unset('thread_count')
        prefs.target_box_enable = False

        redraw_ui(context)

        self.report({'INFO'}, 'Parameters reset')
        return {'FINISHED'}

    def invoke(self, context, event):

        wm = context.window_manager
        pix_per_char = 5
        dialog_width = pix_per_char * len(self.CONFIRMATION_MSG) + 50
        return wm.invoke_props_dialog(self, width=dialog_width)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.CONFIRMATION_MSG)
