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
import multiprocessing
from pathlib import Path

# from .blend import *
from .enums import *
from .utils import get_active_image_size, force_read_int
from .prefs_scripted_utils import scripted_pipeline_property_group
from .labels import Labels
from .contansts import PropConstants
from .mode import ModeType
from .grouping_scheme import UVPM3_GroupingScheme
from .box import UVPM3_Box
from .box_utils import disable_box_rendering
from .island_params import ScaleLimitIParamInfo, AlignPriorityIParamInfo
from .register_utils import UVPM3_OT_SetEnginePath
from .grouping import UVPM3_AutoGroupingOptions
from . import module_loader

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty, PointerProperty
from bpy.types import AddonPreferences
from mathutils import Vector


from .scripted_pipeline import properties
scripted_properties_modules = module_loader.import_submodules(properties)
scripted_properties_classes = module_loader.get_registrable_classes(scripted_properties_modules,
                                                                    sub_class=bpy.types.PropertyGroup,
                                                                    required_vars=("SCRIPTED_PROP_GROUP_ID",))

class UVPM3_DeviceSettings(bpy.types.PropertyGroup):

    enabled : BoolProperty(name='enabled', default=True)

class UVPM3_SavedDeviceSettings(bpy.types.PropertyGroup):

    dev_id : StringProperty(name="", default="")
    settings : PointerProperty(type=UVPM3_DeviceSettings)



def _update_active_main_mode_id(self, context):
    from .panel import UVPM3_PT_Main
    from . import scripted_panels_classes

    bpy.utils.unregister_class(UVPM3_PT_Main)
    bpy.utils.register_class(UVPM3_PT_Main)

    for panel_cls in scripted_panels_classes:
        try:
            bpy.utils.unregister_class(panel_cls)
            bpy.utils.register_class(panel_cls)
        except:
            pass

    disable_box_rendering(None, context)


def _update_engine_status_msg(self, context):
    from .panel import UVPM3_PT_EngineStatus
    try:
        bpy.utils.unregister_class(UVPM3_PT_EngineStatus)
    except:
        pass
    bpy.utils.register_class(UVPM3_PT_EngineStatus)


def _update_orient_3d_axes(self, context):
    if self.orient_prim_3d_axis == self.orient_sec_3d_axis:
        enum_values = self.bl_rna.properties["orient_sec_3d_axis"].enum_items_static.keys()
        value_index = enum_values.index(self.orient_sec_3d_axis)
        self.orient_sec_3d_axis = enum_values[(value_index+1) % len(enum_values)]


class UVPM3_SceneProps(bpy.types.PropertyGroup):

    grouping_schemes : CollectionProperty(name="Grouping Schemes", type=UVPM3_GroupingScheme)
    active_grouping_scheme_idx : IntProperty(default=-1, min=-1, update=disable_box_rendering)

    precision : IntProperty(
        name=Labels.PRECISION_NAME,
        description=Labels.PRECISION_DESC,
        default=500,
        min=10,
        max=10000)

    margin : FloatProperty(
        name=Labels.MARGIN_NAME,
        description=Labels.MARGIN_DESC,
        min=0.0,
        max=0.2,
        default=0.003,
        precision=3,
        step=0.1)

    pixel_margin_enable : BoolProperty(
        name=Labels.PIXEL_MARGIN_ENABLE_NAME,
        description=Labels.PIXEL_MARGIN_ENABLE_DESC,
        default=False)

    pixel_margin : IntProperty(
        name=Labels.PIXEL_MARGIN_NAME,
        description=Labels.PIXEL_MARGIN_DESC,
        min=PropConstants.PIXEL_MARGIN_MIN,
        max=PropConstants.PIXEL_MARGIN_MAX,
        default=PropConstants.PIXEL_MARGIN_DEFAULT)

    pixel_padding : IntProperty(
        name=Labels.PIXEL_PADDING_NAME,
        description=Labels.PIXEL_PADDING_DESC,
        min=PropConstants.PIXEL_PADDING_MIN,
        max=PropConstants.PIXEL_PADDING_MAX,
        default=PropConstants.PIXEL_PADDING_DEFAULT)

    extra_pixel_margin_to_others : IntProperty(
        name=Labels.EXTRA_PIXEL_MARGIN_TO_OTHERS_NAME,
        description=Labels.EXTRA_PIXEL_MARGIN_TO_OTHERS_DESC,
        min=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_MIN,
        max=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_MAX,
        default=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_DEFAULT)

    pixel_margin_tex_size : IntProperty(
        name=Labels.PIXEL_MARGIN_TEX_SIZE_NAME,
        description=Labels.PIXEL_MARGIN_TEX_SIZE_DESC,
        min=PropConstants.PIXEL_MARGIN_TEX_SIZE_MIN,
        max=PropConstants.PIXEL_MARGIN_TEX_SIZE_MAX,
        default=PropConstants.PIXEL_MARGIN_TEX_SIZE_DEFAULT)

    rotation_enable : BoolProperty(
        name=Labels.ROTATION_ENABLE_NAME,
        description=Labels.ROTATION_ENABLE_DESC,
        default=PropConstants.ROTATION_ENABLE_DEFAULT)

    pre_rotation_disable : BoolProperty(
        name=Labels.PRE_ROTATION_DISABLE_NAME,
        description=Labels.PRE_ROTATION_DISABLE_DESC,
        default=PropConstants.PRE_ROTATION_DISABLE_DEFAULT)

    flipping_enable : BoolProperty(
        name=Labels.FLIPPING_ENABLE_NAME,
        description=Labels.FLIPPING_ENABLE_DESC,
        default=PropConstants.FLIPPING_ENABLE_DEFAULT)

    normalize_islands : BoolProperty(
        name=Labels.NORMALIZE_ISLANDS_NAME,
        description=Labels.NORMALIZE_ISLANDS_DESC,
        default=False)

    fixed_scale : BoolProperty(
        name=Labels.FIXED_SCALE_NAME,
        description=Labels.FIXED_SCALE_DESC,
        default=False)

    fixed_scale_strategy : EnumProperty(
        items=UvpmFixedScaleStrategy.to_blend_items(),
        name=Labels.FIXED_SCALE_STRATEGY_NAME,
        description=Labels.FIXED_SCALE_STRATEGY_DESC)

    rotation_step : IntProperty(
        name=Labels.ROTATION_STEP_NAME,
        description=Labels.ROTATION_STEP_DESC,
        default=PropConstants.ROTATION_STEP_DEFAULT,
        min=PropConstants.ROTATION_STEP_MIN,
        max=PropConstants.ROTATION_STEP_MAX)

    island_rot_step_enable : BoolProperty(
        name=Labels.ISLAND_ROT_STEP_ENABLE_NAME,
        description=Labels.ISLAND_ROT_STEP_ENABLE_DESC,
        default=False)

    island_rot_step : IntProperty(
        name=Labels.ISLAND_ROT_STEP_NAME,
        description=Labels.ISLAND_ROT_STEP_DESC,
        default=90,
        min=0,
        max=180)

    island_scale_limit_enable : BoolProperty(
        name=Labels.ISLAND_SCALE_LIMIT_ENABLE_NAME,
        description=Labels.ISLAND_SCALE_LIMIT_ENABLE_DESC,
        default=False)

    island_scale_limit : IntProperty(
        name=Labels.ISLAND_SCALE_LIMIT_NAME,
        description=Labels.ISLAND_SCALE_LIMIT_DESC,
        default=100,
        min=ScaleLimitIParamInfo.MIN_SCALE_LIMIT_VALUE,
        max=ScaleLimitIParamInfo.MAX_SCALE_LIMIT_VALUE)

    tex_ratio : BoolProperty(
        name=Labels.TEX_RATIO_NAME,
        description=Labels.TEX_RATIO_DESC,
        default=False)


    def get_main_mode_blend_enums(scene, context):
        prefs = get_prefs()
        modes_info = prefs.get_modes(ModeType.MAIN)

        return [(mode_id, mode_cls.enum_name(), "") for mode_id, mode_cls in modes_info]

    active_main_mode_id : EnumProperty(
        items=get_main_mode_blend_enums,
        update=_update_active_main_mode_id,
        name=Labels.PACK_MODE_NAME,
        description=Labels.PACK_MODE_DESC)

    group_method : EnumProperty(
        items=GroupingMethod.to_blend_items(),
        name=Labels.GROUP_METHOD_NAME,
        description=Labels.GROUP_METHOD_DESC,
        update=disable_box_rendering)

    auto_group_options : PointerProperty(type=UVPM3_AutoGroupingOptions)

    lock_groups_enable : BoolProperty(
        name=Labels.LOCK_GROUPS_ENABLE_NAME,
        description=Labels.LOCK_GROUPS_ENABLE_DESC,
        default=False)

    lock_group_num : IntProperty(
        name=Labels.LOCK_GROUP_NUM_NAME,
        description=Labels.LOCK_GROUP_NUM_DESC,
        default=1,
        min=1,
        max=100)

    stack_groups_enable : BoolProperty(
        name=Labels.STACK_GROUPS_ENABLE_NAME,
        description=Labels.STACK_GROUPS_ENABLE_DESC,
        default=False)

    stack_group_num : IntProperty(
        name=Labels.STACK_GROUP_NUM_NAME,
        description=Labels.STACK_GROUP_NUM_DESC,
        default=1,
        min=1,
        max=100)

    use_blender_tile_grid : BoolProperty(
        name=Labels.USE_BLENDER_TILE_GRID_NAME,
        description=Labels.USE_BLENDER_TILE_GRID_DESC,
        default=False)

    lock_overlapping_enable : BoolProperty(
        name=Labels.LOCK_OVERLAPPING_ENABLE_NAME,
        description=Labels.LOCK_OVERLAPPING_ENABLE_DESC,
        default=False)

    lock_overlapping_mode : EnumProperty(
        items=UvpmLockOverlappingMode.to_blend_items(),
        name=Labels.LOCK_OVERLAPPING_MODE_NAME,
        description=Labels.LOCK_OVERLAPPING_MODE_DESC)

    heuristic_enable : BoolProperty(
        name=Labels.HEURISTIC_ENABLE_NAME,
        description=Labels.HEURISTIC_ENABLE_DESC,
        default=False)

    heuristic_search_time : IntProperty(
        name=Labels.HEURISTIC_SEARCH_TIME_NAME,
        description=Labels.HEURISTIC_SEARCH_TIME_DESC,
        default=0,
        min=0,
        max=3600)

    heuristic_max_wait_time : IntProperty(
        name=Labels.HEURISTIC_MAX_WAIT_TIME_NAME,
        description=Labels.HEURISTIC_MAX_WAIT_TIME_DESC,
        default=0,
        min=0,
        max=300)

    advanced_heuristic : BoolProperty(
        name=Labels.ADVANCED_HEURISTIC_NAME,
        description=Labels.ADVANCED_HEURISTIC_DESC,
        default=False)

    fully_inside : BoolProperty(
        name=Labels.FULLY_INSIDE_NAME,
        description=Labels.FULLY_INSIDE_DESC,
        default=True)

    move_islands : BoolProperty(
        name=Labels.MOVE_ISLANDS_NAME,
        description=Labels.MOVE_ISLANDS_DESC,
        default=False)

    custom_target_box_enable : BoolProperty(
        name=Labels.CUSTOM_TARGET_BOX_ENABLE_NAME,
        description=Labels.CUSTOM_TARGET_BOX_ENABLE_DESC,
        default=False,
        update=disable_box_rendering)
    
    custom_target_box : PointerProperty(type=UVPM3_Box)

    tile_count_x : IntProperty(
        name='Tile Count (X)',
        description='Number of tiles to use in the X direction',
        default=1,
        min=1,
        max=100)

    tile_count_y : IntProperty(
        name='Tile Count (Y)',
        description='Number of tiles to use in the Y direction',
        default=1,
        min=1,
        max=100)


    # ------ Aligning properties ------ #

    simi_mode : EnumProperty(
        items=UvpmSimilarityMode.to_blend_items(),
        name=Labels.SIMI_MODE_NAME,
        description=Labels.SIMI_MODE_DESC)

    simi_threshold : FloatProperty(
        name=Labels.SIMI_THRESHOLD_NAME,
        description=Labels.SIMI_THRESHOLD_DESC,
        default=0.1,
        min=0.0,
        precision=2,
        step=5.0)

    simi_adjust_scale : BoolProperty(
        name=Labels.SIMI_ADJUST_SCALE_NAME,
        description=Labels.SIMI_ADJUST_SCALE_DESC,
        default=False)

    simi_match_3d_axis : EnumProperty(
        items=UvpmAxis.to_blend_items(include_none=True, only_positive=True),
        name=Labels.SIMI_MATCH_3D_AXIS_NAME,
        description=Labels.SIMI_MATCH_3D_AXIS_DESC)

    simi_match_3d_axis_space : EnumProperty(
        items=UvpmCoordSpace.to_blend_items(),
        name=Labels.SIMI_MATCH_3D_AXIS_SPACE_NAME,
        description=Labels.SIMI_MATCH_3D_AXIS_SPACE_DESC)

    simi_correct_vertices : BoolProperty(
        name=Labels.SIMI_CORRECT_VERTICES_NAME,
        description=Labels.SIMI_CORRECT_VERTICES_DESC,
        default=False)

    simi_vertex_threshold : FloatProperty(
        name=Labels.SIMI_VERTEX_THRESHOLD_NAME,
        description=Labels.SIMI_VERTEX_THRESHOLD_DESC,
        default=0.01,
        min=0.0,
        max=0.05,
        precision=4,
        step=1.0e-1)

    align_priority_enable : BoolProperty(
        name=Labels.ALIGN_PRIORITY_ENABLE_NAME,
        description=Labels.ALIGN_PRIORITY_ENABLE_DESC,
        default=False)

    align_priority : IntProperty(
        name=Labels.ALIGN_PRIORITY_NAME,
        description=Labels.ALIGN_PRIORITY_DESC,
        default=int(AlignPriorityIParamInfo.DEFAULT_VALUE),
        min=int(AlignPriorityIParamInfo.MIN_VALUE),
        max=int(AlignPriorityIParamInfo.MAX_VALUE))

    orient_prim_3d_axis : EnumProperty(
        items=UvpmAxis.to_blend_items(include_none=False, only_positive=True),
        default=PropConstants.ORIENT_PRIM_3D_AXIS_DEFAULT,
        update=_update_orient_3d_axes,
        name=Labels.ORIENT_PRIM_3D_AXIS_NAME,
        description=Labels.ORIENT_PRIM_3D_AXIS_DESC)

    orient_prim_uv_axis : EnumProperty(
        items=UvpmAxis.to_blend_items(include_none=False, only_2d=True),
        default=PropConstants.ORIENT_PRIM_UV_AXIS_DEFAULT,
        name=Labels.ORIENT_PRIM_UV_AXIS_NAME,
        description=Labels.ORIENT_PRIM_UV_AXIS_DESC)

    orient_sec_3d_axis : EnumProperty(
        items=UvpmAxis.to_blend_items(include_none=False, only_positive=True),
        default=PropConstants.ORIENT_SEC_3D_AXIS_DEFAULT,
        update=_update_orient_3d_axes,
        name=Labels.ORIENT_SEC_3D_AXIS_NAME,
        description=Labels.ORIENT_SEC_3D_AXIS_DESC)

    orient_sec_uv_axis : EnumProperty(
        items=UvpmAxis.to_blend_items(include_none=False, only_2d=True),
        default=PropConstants.ORIENT_SEC_UV_AXIS_DEFAULT,
        name=Labels.ORIENT_SEC_UV_AXIS_NAME,
        description=Labels.ORIENT_SEC_UV_AXIS_DESC)

    orient_to_3d_axes_space : EnumProperty(
        items=UvpmCoordSpace.to_blend_items(),
        name=Labels.ORIENT_TO_3D_AXES_SPACE_NAME,
        description=Labels.ORIENT_TO_3D_AXES_SPACE_DESC)

    orient_prim_sec_bias : IntProperty(
        name=Labels.ORIENT_PRIM_SEC_BIAS_NAME,
        description=Labels.ORIENT_PRIM_SEC_BIAS_DESC,
        default=PropConstants.ORIENT_PRIM_SEC_BIAS_DEFAULT,
        min=0,
        max=90)


    def auto_grouping_enabled(self):

        return GroupingMethod.auto_grouping_enabled(self.group_method)

    def active_grouping_scheme(self, context):

        if self.auto_grouping_enabled():
            return None

        from .grouping_scheme import GroupingSchemeAccess
        g_access = GroupingSchemeAccess()
        g_access.init_access(context, ui_drawing=True)
        return g_access.active_g_scheme


class UVPM3_Preferences(AddonPreferences):
    bl_idname = __package__

    MAX_TILES_IN_ROW = 1000

    modes_dict = None

    def pixel_margin_enabled(self, scene_props):
        return scene_props.pixel_margin_enable

    def add_pixel_margin_to_others_enabled(self, scene_props):
        return scene_props.extra_pixel_margin_to_others > 0

    def pixel_padding_enabled(self, scene_props):
        return scene_props.pixel_padding > 0
           
    def heuristic_supported(self, scene_props):

        return True, ''

    def heuristic_enabled(self, scene_props):
        return self.heuristic_supported(scene_props)[0] and scene_props.heuristic_enable

    def heuristic_timeout_enabled(self, scene_props):
        return self.heuristic_enabled(scene_props) and scene_props.heuristic_search_time > 0

    def advanced_heuristic_available(self, scene_props):
        return self.FEATURE_advanced_heuristic and self.heuristic_enabled(scene_props)

    def pack_to_others_supported(self, scene_props):

        return True, ''

    def pack_ratio_supported(self):
        return self.FEATURE_pack_ratio and self.FEATURE_target_box

    def pack_ratio_enabled(self, scene_props):
        return self.pack_ratio_supported() and scene_props.tex_ratio

    def pixel_margin_tex_size(self, scene_props, context):
        if self.pack_ratio_enabled(scene_props):
            img_size = get_active_image_size(context)
            tex_size = img_size[1]
        else:
            tex_size = scene_props.pixel_margin_tex_size

        return tex_size

    def fixed_scale_supported(self, scene_props):
        return True, ''

    def fixed_scale_enabled(self, scene_props):
        return self.fixed_scale_supported(scene_props)[0] and scene_props.fixed_scale

    def normalize_islands_supported(self, scene_props):
        if self.fixed_scale_enabled(scene_props):
            return False, "(Not supported with 'Fixed Scale' enabled)"

        return True, ''

    def normalize_islands_enabled(self, scene_props):
        return self.normalize_islands_supported(scene_props)[0] and scene_props.normalize_islands

    def reset_box_params(self):
        self.box_rendering = False
        self.group_scheme_boxes_editing = False
        self.custom_target_box_editing = False
        self.boxes_dirty = False

    def reset_feature_codes(self):
        self.FEATURE_demo = False
        self.FEATURE_island_rotation = True
        self.FEATURE_overlap_check = True
        self.FEATURE_packing_depth = True
        self.FEATURE_heuristic_search = True
        self.FEATURE_pack_ratio = True
        self.FEATURE_pack_to_others = True
        self.FEATURE_grouping = True
        self.FEATURE_lock_overlapping = True
        self.FEATURE_advanced_heuristic = True
        self.FEATURE_self_intersect_processing = True
        self.FEATURE_validation = True
        self.FEATURE_multi_device_pack = True
        self.FEATURE_target_box = True
        self.FEATURE_island_rotation_step = True
        self.FEATURE_pack_to_tiles = True

    def reset_stats(self):

        for dev in self.device_array():
            dev.reset()

    def reset(self):
        self.engine_path = ''
        self.enabled = True
        self.engine_initialized = False
        self.engine_status_msg = ''
        self.thread_count = multiprocessing.cpu_count()
        self.operation_counter = -1
        self.write_to_file = False
        self.seed = 0

        self.hide_engine_status_panel = self.hide_engine_status_panel_view
        
        self.reset_stats()
        self.reset_device_array()
        self.reset_box_params()
        self.reset_feature_codes()

    def draw_engine_status(self, layout):
        row = layout.row(align=True)
        self.draw_engine_status_message(row, icon_only=False)
        self.draw_engine_status_help_button(row)

    def draw_engine_status_message(self, layout, icon_only):
        icon = 'ERROR' if not self.engine_initialized else 'NONE'
        layout.label(text="" if icon_only else self.engine_status_msg, icon=icon)

    def draw_engine_status_help_button(self, layout):
        if not self.engine_initialized:
            from .operator import UVPM3_OT_SetupHelp
            layout.operator(UVPM3_OT_SetupHelp.bl_idname, icon='QUESTION', text='')

    def draw_addon_options(self, layout):
        col = layout.column(align=True)
        col.label(text='General options:')

        row = col.row(align=True)
        row.prop(self, "thread_count")

        box = col.box()
        row = box.row(align=True)
        row.prop(self, 'orient_aware_uv_islands')

        col.separator()
        col.label(text='UI options:')

        box = col.box()
        row = box.row(align=True)
        row.prop(self, "hide_engine_status_panel_view")

        if self.hide_engine_status_panel_view != self.hide_engine_status_panel:
            box.label(text='Blender restart is required for the change to take effect.', icon='ERROR')
            if self.hide_engine_status_panel_view:
                box.label(text='After the panel is hidden, all its functionalities will be still',)
                box.label(text='available in the addon preferences.')

        box = col.box()
        row = box.row(align=True)
        row.prop(self, 'append_mode_name_to_op_label')

        row = col.row(align=True)
        row.prop(self, "font_size_text_output")

        row = col.row(align=True)
        row.prop(self, "font_size_uv_overlay")

        row = col.row(align=True)
        row.prop(self, "box_render_line_width")

        # adv_op_box = col.box()
        adv_op_layout = col # adv_op_box.column(align=True)
        adv_op_layout.separator()
        adv_op_layout.label(text='Expert options:')

        UVPM3_OT_ShowHideAdvancedOptions.draw_operator(adv_op_layout)
        if self.show_expert_options:
            box = adv_op_layout.box()
            box.label(text='Change expert options only if you really know what you are doing.', icon='ERROR')

            box = adv_op_layout.box()
            row = box.row(align=True)
            row.prop(self, 'disable_immediate_uv_update')

    def draw(self, context):
        layout = self.layout

        # main_box = layout.box()
        main_col = layout.column(align=True)
        main_col.label(text='Engine status:')
        box = main_col.box()
        self.draw_engine_status(box)
        
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Path to the UVPM engine:")
        row = col.row(align=True)
        row.enabled = False
        row.prop(self, 'engine_path')

        row = col.row(align=True)
        row.operator(UVPM3_OT_SetEnginePath.bl_idname)

        main_col.separator()
        main_col.separator()

        self.draw_addon_options(main_col)

        main_col.separator()
        main_col.separator()

        main_col.label(text='Packing devices:')
        dev_main = main_col.column(align=True)
        dev_table_header = dev_main.box()
        row = dev_table_header.row()

        row.label(text='Name')
        row.label(text='Enabled')
        dev_table = dev_main.box()

        for dev in self.device_array():
            settings = dev.settings
            row = dev_table.row()
            row.label(text=dev.name)
            row.prop(settings, 'enabled', text=' ')


    def get_mode(self, mode_id, context):
        if self.modes_dict is None:
            raise RuntimeError("Mods are not initialized.")
        try:
            return next(m(context) for m_list in self.modes_dict.values() for (m_id, m) in m_list if m_id == mode_id)
        except StopIteration:
            raise KeyError("The '{}' mode not found".format(mode_id))

    def get_modes(self, mode_type):
        return self.modes_dict[mode_type]

    def get_active_main_mode(self, scene_props, context):
        return self.get_mode(scene_props.active_main_mode_id, context)

    # Supporeted features
    FEATURE_demo : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_island_rotation : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_overlap_check : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_packing_depth : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_heuristic_search : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_advanced_heuristic : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_ratio : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_to_others : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_grouping : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_lock_overlapping : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_self_intersect_processing : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_validation : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_multi_device_pack : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_target_box : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_island_rotation_step : BoolProperty(
        name='',
        description='',
        default=False)

    FEATURE_pack_to_tiles : BoolProperty(
        name='',
        description='',
        default=False)

    operation_counter : IntProperty(
        name='',
        description='',
        default=-1)

    box_rendering : BoolProperty(
        name='',
        description='',
        default=False)

    boxes_dirty : BoolProperty(
        name='',
        description='',
        default=False)

    group_scheme_boxes_editing : BoolProperty(
        name='',
        description='',
        default=False)

    custom_target_box_editing : BoolProperty(
        name='',
        description='',
        default=False)

    engine_retcode : IntProperty(
        name='',
        description='',
        default=0)

    engine_path : StringProperty(
        name='',
        description='',
        default='')

    engine_initialized : BoolProperty(
        name='',
        description='',
        default=False)

    engine_status_msg : StringProperty(
        name='',
        description='',
        default='',
        update=_update_engine_status_msg)

    thread_count : IntProperty(
        name=Labels.THREAD_COUNT_NAME,
        description=Labels.THREAD_COUNT_DESC,
        default=multiprocessing.cpu_count(),
        min=1,
        max=multiprocessing.cpu_count())

    seed : IntProperty(
        name=Labels.SEED_NAME,
        description='',
        default=0,
        min=0,
        max=10000)

    test_param : IntProperty(
        name=Labels.TEST_PARAM_NAME,
        description='',
        default=0,
        min=0,
        max=10000)

    write_to_file : BoolProperty(
        name=Labels.WRITE_TO_FILE_NAME,
        description='',
        default=False)

    wait_for_debugger : BoolProperty(
        name=Labels.WAIT_FOR_DEBUGGER_NAME,
        description='',
        default=False)

    append_mode_name_to_op_label : BoolProperty(
        name=Labels.APPEND_MODE_NAME_TO_OP_LABEL_NAME,
        description=Labels.APPEND_MODE_NAME_TO_OP_LABEL_DESC,
        default=False)

    orient_aware_uv_islands : BoolProperty(
        name=Labels.ORIENT_AWARE_UV_ISLANDS_NAME,
        description=Labels.ORIENT_AWARE_UV_ISLANDS_DESC,
        default=False)

    # UI options
    hide_engine_status_panel : BoolProperty(
        name='',
        description='',
        default=False)

    hide_engine_status_panel_view : BoolProperty(
        name=Labels.HIDE_ENGINE_STATUS_PANEL_NAME,
        description=Labels.HIDE_ENGINE_STATUS_PANEL_DESC,
        default=False)

    font_size_text_output : IntProperty(
        name=Labels.FONT_SIZE_TEXT_OUTPUT_NAME,
        description=Labels.FONT_SIZE_TEXT_OUTPUT_DESC,
        default=15,
        min=5,
        max=100)

    font_size_uv_overlay : IntProperty(
        name=Labels.FONT_SIZE_UV_OVERLAY_NAME,
        description=Labels.FONT_SIZE_UV_OVERLAY_DESC,
        default=20,
        min=5,
        max=100)

    box_render_line_width : FloatProperty(
        name=Labels.BOX_RENDER_LINE_WIDTH_NAME,
        description=Labels.BOX_RENDER_LINE_WIDTH_DESC,
        default=4.0,
        min=1.0,
        max=10.0,
        step=5.0)
    
    # Expert options
    show_expert_options : BoolProperty(
        name=Labels.SHOW_EXPERT_OPTIONS_NAME,
        description=Labels.SHOW_EXPERT_OPTIONS_DESC,
        default = False
    )

    disable_immediate_uv_update : BoolProperty(
        name=Labels.DISABLE_IMMEDIATE_UV_UPDATE_NAME,
        description=Labels.DISABLE_IMMEDIATE_UV_UPDATE_DESC,
        default = False
    )


    dev_array = []
    saved_dev_settings : CollectionProperty(type=UVPM3_SavedDeviceSettings)

    def device_array(self):
        return type(self).dev_array

    def reset_device_array(self):
        type(self).dev_array = []

    def get_userdata_path(self):
        from .os_iface import os_get_userdata_path
        os_userdata_path = os_get_userdata_path()
        return os.path.join(os_userdata_path, 'blender', 'engine3')

    def get_main_preset_path(self):
        preset_path = os.path.join(self.get_userdata_path(), 'presets')
        Path(preset_path).mkdir(parents=True, exist_ok=True)
        return preset_path

    def get_grouping_schemes_preset_path(self):
        preset_path = os.path.join(self.get_userdata_path(), 'grouping_schemes')
        Path(preset_path).mkdir(parents=True, exist_ok=True)
        return preset_path



@scripted_pipeline_property_group("scripted_props",
                                  UVPM3_SceneProps, scripted_properties_classes,
                                  (UVPM3_SceneProps, UVPM3_Preferences))
class UVPM3_ScriptedPipelineProperties(bpy.types.PropertyGroup):
    pass


class UVPM3_OT_ShowHideAdvancedOptions(bpy.types.Operator):

    bl_label = 'Show Expert Options'
    bl_idname = 'uvpackmaster3.show_hide_expert_options'

    @staticmethod
    def get_label():
        prefs = get_prefs()
        return 'Hide Expert Options' if prefs.show_expert_options else 'Show Expert Options'

    @classmethod
    def draw_operator(cls, layout):
        layout.operator(cls.bl_idname, text=cls.get_label())

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        for label in self.confirmation_labels:
            col.label(text=label)

    def execute(self, context):
        prefs = get_prefs()
        prefs.show_expert_options = not prefs.show_expert_options

        from .utils import redraw_ui
        redraw_ui(context)

        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = get_prefs()

        if not prefs.show_expert_options:
            self.confirmation_labels =\
                [ 'WARNING: expert options should NEVER be changed under the standard packer usage.',
                  'You should only change them if you really know what you are doing.',
                  'Are you sure you want to show the expert options?' ]

            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=700)

        return self.execute(context)
