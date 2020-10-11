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


import multiprocessing

from .blend import *
from .enums import *
from .labels import UvpLabels

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty
from bpy.types import AddonPreferences
from mathutils import Vector


class UVP2_DeviceDesc(bpy.types.PropertyGroup):
    id = bpy.props.StringProperty(name="", default="")
    name = bpy.props.StringProperty(name="", default="")
    supported = bpy.props.BoolProperty(name="", default=False)
    supports_groups_together = bpy.props.BoolProperty(name="", default=False)

class UVP2_PackStats(bpy.types.PropertyGroup):
    dev_name = bpy.props.StringProperty(name="", default='')
    iter_count = bpy.props.IntProperty(name="", default=0)
    total_time = bpy.props.IntProperty(name="", default=0)
    avg_time = bpy.props.IntProperty(name="", default=0)

class UVP2_SceneProps(bpy.types.PropertyGroup):

    precision = IntProperty(
        name=UvpLabels.PRECISION_NAME,
        description=UvpLabels.PRECISION_DESC,
        default=500,
        min=10,
        max=10000)

    margin = FloatProperty(
        name=UvpLabels.MARGIN_NAME,
        description=UvpLabels.MARGIN_DESC,
        min=0.0,
        default=0.003,
        precision=3,
        step=0.1)

    pixel_margin = IntProperty(
        name=UvpLabels.PIXEL_MARGIN_NAME,
        description=UvpLabels.PIXEL_MARGIN_DESC,
        min=0,
        max=128,
        default=0)

    pixel_padding = IntProperty(
        name=UvpLabels.PIXEL_PADDING_NAME,
        description=UvpLabels.PIXEL_PADDING_DESC,
        min=0,
        max=128,
        default=0)

    pixel_margin_method = EnumProperty(
        items=(UvPixelMarginMethod.ADJUSTMENT_TIME.to_blend_enum(),
               UvPixelMarginMethod.ITERATIVE.to_blend_enum()),
        name=UvpLabels.PIXEL_MARGIN_METHOD_NAME,
        description=UvpLabels.PIXEL_MARGIN_METHOD_DESC)

    pixel_margin_tex_size = IntProperty(
        name=UvpLabels.PIXEL_MARGIN_TEX_SIZE_NAME,
        description=UvpLabels.PIXEL_MARGIN_TEX_SIZE_DESC,
        min=8,
        default=1024)

    rot_enable = BoolProperty(
        name=UvpLabels.ROT_ENABLE_NAME,
        description=UvpLabels.ROT_ENABLE_DESC,
        default=True)

    prerot_disable = BoolProperty(
        name=UvpLabels.PREROT_DISABLE_NAME,
        description=UvpLabels.PREROT_DISABLE_DESC,
        default=False)

    normalize_islands = BoolProperty(
        name=UvpLabels.NORMALIZE_ISLANDS_NAME,
        description=UvpLabels.NORMALIZE_ISLANDS_DESC,
        default=False)

    fixed_scale = BoolProperty(
        name=UvpLabels.FIXED_SCALE_NAME,
        description=UvpLabels.FIXED_SCALE_DESC,
        default=False)

    fixed_scale_strategy = EnumProperty(
        items=UvFixedScaleStrategy.to_blend_enums(),
        name=UvpLabels.FIXED_SCALE_STRATEGY_NAME,
        description=UvpLabels.FIXED_SCALE_STRATEGY_DESC)

    rot_step = IntProperty(
        name=UvpLabels.ROT_STEP_NAME,
        description=UvpLabels.ROT_STEP_DESC,
        default=90,
        min=1,
        max=180)

    island_rot_step_enable = BoolProperty(
        name=UvpLabels.ISLAND_ROT_STEP_ENABLE_NAME,
        description=UvpLabels.ISLAND_ROT_STEP_ENABLE_DESC,
        default=False)

    island_rot_step = IntProperty(
        name=UvpLabels.ISLAND_ROT_STEP_NAME,
        description=UvpLabels.ISLAND_ROT_STEP_DESC,
        default=90,
        min=0,
        max=180)

    tex_ratio = BoolProperty(
        name=UvpLabels.TEX_RATIO_NAME,
        description=UvpLabels.TEX_RATIO_DESC,
        default=False)

    pack_to_others = BoolProperty(
        name=UvpLabels.PACK_TO_OTHERS_NAME,
        description=UvpLabels.PACK_TO_OTHERS_DESC,
        default=False)

    def get_pack_modes(scene, context):
        return UvPackingMode.to_blend_enums()

    pack_mode = EnumProperty(
        items=get_pack_modes,
        name=UvpLabels.PACK_MODE_NAME,
        description=UvpLabels.PACK_MODE_DESC)

    group_method = EnumProperty(
        items=(UvGroupingMethod.MATERIAL.to_blend_enum(),
               UvGroupingMethod.SIMILARITY.to_blend_enum(),
               UvGroupingMethod.MESH.to_blend_enum(),
               UvGroupingMethod.OBJECT.to_blend_enum(),
               UvGroupingMethod.TILE.to_blend_enum(),
               UvGroupingMethod.MANUAL.to_blend_enum()),
        name=UvpLabels.GROUP_METHOD_NAME,
        description=UvpLabels.GROUP_METHOD_DESC)

    group_compactness = FloatProperty(
        name=UvpLabels.GROUP_COMPACTNESS_NAME,
        description=UvpLabels.GROUP_COMPACTNESS_DESC,
        default=0.0,
        min=0.0,
        max=1.0,
        precision=2,
        step=10.0)

    manual_group_num = IntProperty(
        name=UvpLabels.MANUAL_GROUP_NUM_NAME,
        description=UvpLabels.MANUAL_GROUP_NUM_DESC,
        default=0,
        min=0,
        max=100)

    lock_groups_enable = BoolProperty(
        name=UvpLabels.LOCK_GROUPS_ENABLE_NAME,
        description=UvpLabels.LOCK_GROUPS_ENABLE_DESC,
        default=False)

    lock_group_num = IntProperty(
        name=UvpLabels.LOCK_GROUP_NUM_NAME,
        description=UvpLabels.LOCK_GROUP_NUM_DESC,
        default=1,
        min=1,
        max=100)

    use_blender_tile_grid = BoolProperty(
        name=UvpLabels.USE_BLENDER_TILE_GRID_NAME,
        description=UvpLabels.USE_BLENDER_TILE_GRID_DESC,
        default=False)

    tile_count = IntProperty(
        name=UvpLabels.TILE_COUNT_NAME,
        description=UvpLabels.TILE_COUNT_DESC,
        default=2,
        min=0)

    tiles_in_row = IntProperty(
        name=UvpLabels.TILES_IN_ROW_NAME,
        description=UvpLabels.TILES_IN_ROW_DESC,
        default=10,
        min=1)

    lock_overlapping_mode = EnumProperty(
        items=(UvLockOverlappingMode.DISABLED.to_blend_enum(),
               UvLockOverlappingMode.ANY_PART.to_blend_enum(),
               UvLockOverlappingMode.EXACT.to_blend_enum()),
        name=UvpLabels.LOCK_OVERLAPPING_MODE_NAME,
        description=UvpLabels.LOCK_OVERLAPPING_MODE_DESC)

    pre_validate = BoolProperty(
        name=UvpLabels.PRE_VALIDATE_NAME,
        description=UvpLabels.PRE_VALIDATE_DESC,
        default=False)

    heuristic_enable = BoolProperty(
        name=UvpLabels.HEURISTIC_ENABLE_NAME,
        description=UvpLabels.HEURISTIC_ENABLE_DESC,
        default=False)

    heuristic_search_time = IntProperty(
        name=UvpLabels.HEURISTIC_SEARCH_TIME_NAME,
        description=UvpLabels.HEURISTIC_SEARCH_TIME_DESC,
        default=0,
        min=0)

    heuristic_max_wait_time = IntProperty(
        name=UvpLabels.HEURISTIC_MAX_WAIT_TIME_NAME,
        description=UvpLabels.HEURISTIC_MAX_WAIT_TIME_DESC,
        default=0,
        min=0)

    pixel_margin_adjust_time = IntProperty(
        name=UvpLabels.PIXEL_MARGIN_ADJUST_TIME_NAME,
        description=UvpLabels.PIXEL_MARGIN_ADJUST_TIME_DESC,
        default=1,
        min=1,
        max=1000)

    advanced_heuristic = BoolProperty(
        name=UvpLabels.ADVANCED_HEURISTIC_NAME,
        description=UvpLabels.ADVANCED_HEURISTIC_DESC,
        default=False)

    similarity_threshold = FloatProperty(
        name=UvpLabels.SIMILARITY_THRESHOLD_NAME,
        description=UvpLabels.SIMILARITY_THRESHOLD_DESC,
        default=0.5,
        min=0.0,
        precision=2,
        step=5.0)

    multi_device_pack = BoolProperty(
        name=UvpLabels.MULTI_DEVICE_PACK_NAME,
        description=UvpLabels.MULTI_DEVICE_PACK_DESC,
        default=True)

    fully_inside = BoolProperty(
        name=UvpLabels.FULLY_INSIDE_NAME,
        description=UvpLabels.FULLY_INSIDE_DESC,
        default=True)

    move_islands = BoolProperty(
        name=UvpLabels.MOVE_ISLANDS_NAME,
        description=UvpLabels.MOVE_ISLANDS_DESC,
        default=False)

    target_box_tile_x = IntProperty(
        name=UvpLabels.TARGET_BOX_TILE_X_NAME,
        description=UvpLabels.TARGET_BOX_TILE_X_DESC,
        default=0)

    target_box_tile_y = IntProperty(
        name=UvpLabels.TARGET_BOX_TILE_Y_NAME,
        description=UvpLabels.TARGET_BOX_TILE_Y_DESC,
        default=0)

    target_box_p1_x = FloatProperty(
        name=UvpLabels.TARGET_BOX_P1_X_NAME,
        description=UvpLabels.TARGET_BOX_P1_X_DESC,
        default=0.0,
        precision=3,
        step=10.0)

    target_box_p1_y = FloatProperty(
        name=UvpLabels.TARGET_BOX_P1_Y_NAME,
        description=UvpLabels.TARGET_BOX_P1_Y_DESC,
        default=0.0,
        precision=3,
        step=10.0)

    target_box_p2_x = FloatProperty(
        name=UvpLabels.TARGET_BOX_P2_X_NAME,
        description=UvpLabels.TARGET_BOX_P1_X_DESC,
        default=1.0,
        precision=3,
        step=10.0)

    target_box_p2_y = FloatProperty(
        name=UvpLabels.TARGET_BOX_P2_Y_NAME,
        description=UvpLabels.TARGET_BOX_P1_Y_DESC,
        default=1.0,
        precision=3,
        step=10.0)


class UVP2_Preferences(AddonPreferences):
    bl_idname = __package__

    MAX_TILES_IN_ROW = 1000

    def pixel_margin_enabled(self, scene_props):
        return scene_props.pixel_margin > 0

    def pixel_padding_enabled(self, scene_props):
        return scene_props.pixel_padding > 0

    def pixel_margin_method_enabled(self, scene_props, context):
        if self.fixed_scale_enabled(scene_props):
            return False, "'Fixed Scale' always provides exact pixel margin"

        if self.pack_to_others_enabled(scene_props):
            return False, "'Pack To Others' always uses the 'Iterative' method"

        tile_count, tiles_in_row = self.tile_grid_config(scene_props, context)

        if self.pack_to_tiles(scene_props) and tile_count != 1:
            return False, "Packing mode 'Tiles' always uses the 'Iterative' method, unless 'Tile Count' is set to 1"

        if self.pack_groups_together(scene_props):
            return False, "Packing mode 'Groups Together' always uses the 'Iterative' method"

        return True, ''

    def pixel_margin_adjust_time_enabled(self, scene_props):
        return scene_props.pixel_margin_method == UvPixelMarginMethod.ADJUSTMENT_TIME.code

    def pixel_margin_iterative_enabled(self, scene_props):
        return scene_props.pixel_margin_method == UvPixelMarginMethod.ITERATIVE.code

    def pack_to_tiles(self, scene_props):
        return self.FEATURE_pack_to_tiles and scene_props.pack_mode == UvPackingMode.TILES.code

    def tile_grid_config(self, scene_props, context):
        tile_grid_shape = None

        if scene_props.use_blender_tile_grid:
            try:
                tile_grid_shape = context.space_data.uv_editor.tile_grid_shape
            except:
                pass

        if tile_grid_shape is None:
            tile_count = scene_props.tile_count
            tiles_in_row = scene_props.tiles_in_row
        else:
            tile_count = tile_grid_shape[0] * tile_grid_shape[1]
            tiles_in_row = tile_grid_shape[0]

        if self.grouping_enabled(scene_props) and scene_props.group_method == UvGroupingMethod.TILE.code:
            tiles_in_row = self.MAX_TILES_IN_ROW

        return (tile_count, tiles_in_row)

    def grouping_enabled(self, scene_props):
        return self.FEATURE_grouping and (scene_props.pack_mode == UvPackingMode.GROUPS_TOGETHER.code or scene_props.pack_mode == UvPackingMode.GROUPS_TO_TILES.code)

    def pack_groups_together(self, scene_props):
        return self.grouping_enabled(scene_props) and (scene_props.pack_mode == UvPackingMode.GROUPS_TOGETHER.code)

    def pack_groups_to_tiles(self, scene_props):
        return self.grouping_enabled(scene_props) and (scene_props.pack_mode == UvPackingMode.GROUPS_TO_TILES.code)

    def tiles_enabled(self, scene_props):
        return self.pack_to_tiles(scene_props) or self.pack_groups_to_tiles(scene_props)

    def multi_device_enabled(self, scene_props):
        return (self.FEATURE_multi_device_pack and scene_props.multi_device_pack)
                 
    def heuristic_supported(self, scene_props):
        if not self.FEATURE_heuristic_search:
            return False , UvpLabels.FEATURE_NOT_SUPPORTED_MSG

        pack_mode = UvPackingMode.get_mode(scene_props.pack_mode)

        if not pack_mode.supports_heuristic:
            return False, UvpLabels.FEATURE_NOT_SUPPORTED_BY_PACKING_MODE_MSG

        return True, ''

    def heuristic_enabled(self, scene_props):
        return self.heuristic_supported(scene_props)[0] and scene_props.heuristic_enable

    def heuristic_timeout_enabled(self, scene_props):
        return self.heuristic_enabled(scene_props) and scene_props.heuristic_search_time > 0

    def advanced_heuristic_available(self, scene_props):
        return self.FEATURE_advanced_heuristic and self.heuristic_enabled(scene_props)

    def pack_to_others_supported(self, scene_props):
        if not self.FEATURE_pack_to_others:
            return False, UvpLabels.FEATURE_NOT_SUPPORTED_MSG

        pack_mode = UvPackingMode.get_mode(scene_props.pack_mode)

        if not pack_mode.supports_pack_to_others:
            return False, UvpLabels.FEATURE_NOT_SUPPORTED_BY_PACKING_MODE_MSG

        return True, ''

    def pack_to_others_enabled(self, scene_props):
        return self.pack_to_others_supported(scene_props)[0] and scene_props.pack_to_others

    def pack_ratio_supported(self):
        return self.FEATURE_pack_ratio and self.FEATURE_target_box

    def pack_ratio_enabled(self, scene_props):
        return self.pack_ratio_supported() and scene_props.tex_ratio

    def fixed_scale_supported(self, scene_props):
        pack_mode = UvPackingMode.get_mode(scene_props.pack_mode)

        if not pack_mode.supports_fixed_scale:
            return False, UvpLabels.FEATURE_NOT_SUPPORTED_BY_PACKING_MODE_MSG

        return True, ''

    def fixed_scale_enabled(self, scene_props):
        return self.fixed_scale_supported(scene_props)[0] and scene_props.fixed_scale

    def normalize_islands_supported(self, scene_props):
        if self.fixed_scale_enabled(scene_props):
            return False, "(Not supported with 'Fixed Scale' enabled)"

        return True, ''

    def normalize_islands_enabled(self, scene_props):
        return self.normalize_islands_supported(scene_props)[0] and scene_props.normalize_islands

    def lock_overlap_enabled(self, scene_props):
        return self.FEATURE_lock_overlapping and scene_props.lock_overlapping_mode != UvLockOverlappingMode.DISABLED.code

    def target_box(self, scene_props):
        x_min = min(scene_props.target_box_p1_x, scene_props.target_box_p2_x)
        x_max = max(scene_props.target_box_p1_x, scene_props.target_box_p2_x)

        y_min = min(scene_props.target_box_p1_y, scene_props.target_box_p2_y)
        y_max = max(scene_props.target_box_p1_y, scene_props.target_box_p2_y)

        return (Vector((x_min, y_min)), Vector((x_max, y_max)))

    def reset_target_box(self, scene_props):

        scene_props.target_box_p1_x = 0.0
        scene_props.target_box_p1_y = 0.0

        scene_props.target_box_p2_x = 1.0
        scene_props.target_box_p2_y = 1.0


    # Supporeted features
    FEATURE_demo = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_island_rotation = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_overlap_check = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_packing_depth = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_heuristic_search = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_advanced_heuristic = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_ratio = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_to_others = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_grouping = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_lock_overlapping = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_self_intersect_processing = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_validation = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_multi_device_pack = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_target_box = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_island_rotation_step = BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_to_tiles = BoolProperty(
        name='',
        description='',
        default=False)

    target_box_enable = BoolProperty(
        name='',
        description='',
        default=False)

    target_box_draw_enable = BoolProperty(
        name='',
        description='',
        default=False)

    uvp_retcode = IntProperty(
        name='',
        description='',
        default=0)

    uvp_path = StringProperty(
        name='',
        description='',
        default='')

    uvp_initialized = BoolProperty(
        name='',
        description='',
        default=False)

    label_message = StringProperty(
        name='',
        description='',
        default='')

    thread_count = IntProperty(
        name=UvpLabels.THREAD_COUNT_NAME,
        description=UvpLabels.THREAD_COUNT_DESC,
        default=multiprocessing.cpu_count(),
        min=1,
        max=multiprocessing.cpu_count())

    packing_depth = IntProperty(
        name=UvpLabels.PACKING_DEPTH_NAME,
        description='',
        default=1,
        min=1,
        max=100)

    seed = IntProperty(
        name=UvpLabels.SEED_NAME,
        description='',
        default=0,
        min=0,
        max=10000)

    test_param = IntProperty(
        name=UvpLabels.TEST_PARAM_NAME,
        description='',
        default=0,
        min=0,
        max=10000)

    write_to_file = BoolProperty(
        name=UvpLabels.WRITE_TO_FILE_NAME,
        description='',
        default=False)

    simplify_disable = BoolProperty(
        name=UvpLabels.SIMPLIFY_DISABLE_NAME,
        description='',
        default=False)

    wait_for_debugger = BoolProperty(
        name=UvpLabels.WAIT_FOR_DEBUGGER_NAME,
        description='',
        default=False)

    sel_dev_idx = IntProperty(name="", default=0)
    supported_dev_count = IntProperty(name="", default=0)

    stats_area = FloatProperty(default=-1.0)





