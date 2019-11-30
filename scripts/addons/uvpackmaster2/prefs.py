
import multiprocessing

from .blend import *
from .enums import *
from .labels import UvpLabels

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty
from bpy.types import AddonPreferences


class UVP2_DeviceDesc(bpy.types.PropertyGroup):
    id = bpy.props.StringProperty(name="", default="")
    name = bpy.props.StringProperty(name="", default="")
    supported = bpy.props.BoolProperty(name="", default=False)
    supports_groups_together = bpy.props.BoolProperty(name="", default=False)

class UVP2_PackStats(bpy.types.PropertyGroup):
    iter_count = bpy.props.IntProperty(name="", default=0)
    total_time = bpy.props.IntProperty(name="", default=0)
    avg_time = bpy.props.IntProperty(name="", default=0)

class UVP2_SceneProps(bpy.types.PropertyGroup):

    overlap_check = BoolProperty(
        name=UvpLabels.OVERLAP_CHECK_NAME,
        description=UvpLabels.OVERLAP_CHECK_DESC,
        default=True)

    area_measure = BoolProperty(
        name=UvpLabels.AREA_MEASURE_NAME,
        description=UvpLabels.AREA_MEASURE_DESC,
        default=True)

    precision = IntProperty(
        name=UvpLabels.PRECISION_NAME,
        description=UvpLabels.PRECISION_DESC,
        default=200,
        min=10,
        max=10000)

    margin = FloatProperty(
        name=UvpLabels.MARGIN_NAME,
        description=UvpLabels.MARGIN_DESC,
        min=0.0,
        default=0.005,
        precision=3)

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

    postscale_disable = BoolProperty(
        name=UvpLabels.POSTSCALE_DISABLE_NAME,
        description=UvpLabels.POSTSCALE_DISABLE_DESC,
        default=False)

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
               UvGroupingMethod.OBJECT.to_blend_enum()),
        name=UvpLabels.GROUP_METHOD_NAME,
        description=UvpLabels.GROUP_METHOD_DESC)

    tiles_in_row = IntProperty(
        name=UvpLabels.TILES_IN_ROW_NAME,
        description=UvpLabels.TILES_IN_ROW_DESC,
        default=10,
        min=1)

    lock_overlapping = BoolProperty(
        name=UvpLabels.LOCK_OVERLAPPING_NAME,
        description=UvpLabels.LOCK_OVERLAPPING_DESC,
        default=False)

    pre_validate = BoolProperty(
        name=UvpLabels.PRE_VALIDATE_NAME,
        description=UvpLabels.PRE_VALIDATE_DESC,
        default=False)

    heuristic_enable = BoolProperty(
        name=UvpLabels.HEURISTIC_ENABLE_NAME,
        description=UvpLabels.HEURISTIC_ENABLE_DESC,
        default=False)

    heuristic_search_time = IntProperty(
        name=UvpLabels.HEURISTIC_SEACH_TIME_NAME,
        description=UvpLabels.HEURISTIC_SEACH_TIME_DESC,
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
        precision=3)

    multi_device_pack = BoolProperty(
        name=UvpLabels.MULTI_DEVICE_PACK_NAME,
        description=UvpLabels.MULTI_DEVICE_PACK_DESC,
        default=True)

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
        precision=3)

    target_box_p1_y = FloatProperty(
        name=UvpLabels.TARGET_BOX_P1_Y_NAME,
        description=UvpLabels.TARGET_BOX_P1_Y_DESC,
        default=0.0,
        precision=3)

    target_box_p2_x = FloatProperty(
        name=UvpLabels.TARGET_BOX_P2_X_NAME,
        description=UvpLabels.TARGET_BOX_P1_X_DESC,
        default=1.0,
        precision=3)

    target_box_p2_y = FloatProperty(
        name=UvpLabels.TARGET_BOX_P2_Y_NAME,
        description=UvpLabels.TARGET_BOX_P1_Y_DESC,
        default=1.0,
        precision=3)


class UVP2_Preferences(AddonPreferences):
    bl_idname = __package__

    def pixel_margin_enabled(self, scene_props):
        return scene_props.pixel_margin > 0

    def pixel_padding_enabled(self, scene_props):
        return scene_props.pixel_padding > 0

    def pack_to_tiles_fixed_scale(self, scene_props):
        return self.FEATURE_pack_to_tiles and scene_props.pack_mode == UvPackingMode.TILES_FIXED_SCALE.code

    def grouping_enabled(self, scene_props):
        return self.FEATURE_grouping and (scene_props.pack_mode == UvPackingMode.GROUPS_TOGETHER.code or scene_props.pack_mode == UvPackingMode.GROUPS_TO_TILES.code)

    def pack_groups_together(self, scene_props):
        return self.grouping_enabled(scene_props) and (scene_props.pack_mode == UvPackingMode.GROUPS_TOGETHER.code)

    def pack_groups_to_tiles(self, scene_props):
        return self.grouping_enabled(scene_props) and (scene_props.pack_mode == UvPackingMode.GROUPS_TO_TILES.code)

    def pack_to_tiles(self, scene_props):
        return self.pack_to_tiles_fixed_scale(scene_props) or self.pack_groups_to_tiles(scene_props)

    def multi_device_enabled(self, scene_props):
        return (self.FEATURE_multi_device_pack and scene_props.multi_device_pack) and\
                (self.heuristic_enabled(scene_props) or self.pack_groups_to_tiles(scene_props))
                 
    def heuristic_enabled(self, scene_props):
        return self.FEATURE_heuristic_search and scene_props.heuristic_enable

    def heuristic_timeout_enabled(self, scene_props):
        return self.heuristic_enabled(scene_props) and scene_props.heuristic_search_time > 0

    def advanced_heuristic_available(self, scene_props):
        return self.FEATURE_advanced_heuristic and self.heuristic_enabled(scene_props)

    def pack_to_others_enabled(self, scene_props):
        return self.FEATURE_pack_to_others and scene_props.pack_to_others

    def pack_ratio_supported(self):
        return self.FEATURE_pack_ratio and self.FEATURE_target_box

    def pack_ratio_enabled(self, scene_props):
        return self.pack_ratio_supported() and scene_props.tex_ratio

    def packing_scales_islands(self, scene_props):
        return not self.pack_to_others_enabled(scene_props) and not self.pack_to_tiles_fixed_scale(scene_props) and not scene_props.postscale_disable

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

    DISABLED_rot_enable = BoolProperty(
        name=UvpLabels.ROT_ENABLE_NAME,
        description=UvpLabels.ROT_ENABLE_DESC,
        default=False)

    DISABLED_overlap_check = BoolProperty(
        name=UvpLabels.OVERLAP_CHECK_NAME,
        description=UvpLabels.OVERLAP_CHECK_DESC,
        default=False)

    DISABLED_pre_validate = BoolProperty(
        name=UvpLabels.PRE_VALIDATE_NAME,
        description=UvpLabels.PRE_VALIDATE_DESC,
        default=False)

    DISABLED_heuristic_enable = BoolProperty(
        name=UvpLabels.HEURISTIC_ENABLE_NAME,
        description=UvpLabels.HEURISTIC_ENABLE_DESC,
        default=False)

    DISABLED_advanced_heuristic = BoolProperty(
        name=UvpLabels.ADVANCED_HEURISTIC_NAME,
        description=UvpLabels.ADVANCED_HEURISTIC_DESC,
        default=False)

    DISABLED_multi_device_pack = BoolProperty(
        name=UvpLabels.MULTI_DEVICE_PACK_NAME,
        description=UvpLabels.MULTI_DEVICE_PACK_DESC,
        default=False)

    DISABLED_tex_ratio = BoolProperty(
        name=UvpLabels.TEX_RATIO_NAME,
        description=UvpLabels.TEX_RATIO_DESC,
        default=False)

    DISABLED_pack_to_others = BoolProperty(
        name=UvpLabels.PACK_TO_OTHERS_NAME,
        description=UvpLabels.PACK_TO_OTHERS_DESC,
        default=False)

    DISABLED_lock_overlapping = BoolProperty(
        name=UvpLabels.LOCK_OVERLAPPING_NAME,
        description=UvpLabels.LOCK_OVERLAPPING_DESC,
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





