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

from ...operator_box import GroupingSchemeRenderAccess
from ...prefs_scripted_utils import ScriptParams
from ...mode import UVPM3_Mode_Main, UVPM3_ModeCategory_Packing, OperatorMetadata
from ..operators.pack_operator import UVPM3_OT_Pack
from ...box import DEFAULT_TARGET_BOX
from ...box_utils import BoxRenderer, BoxArrayRenderAccess, CustomTargetBoxAccess
from ...island_params import ScaleLimitIParamInfo, VColorIParamSerializer, RotStepIParamInfo, LockGroupIParamInfo
from ...utils import get_active_image_ratio

from ..panels.pack_panels import (
        UVPM3_PT_TileLayout,
        UVPM3_PT_PackOptions,
        UVPM3_PT_PixelMargin,
        UVPM3_PT_Heuristic,
        UVPM3_PT_NonSquarePacking,
        UVPM3_PT_TargetBox,
        UVPM3_PT_IslandRotStep,
        UVPM3_PT_IslandScaleLimit,
        UVPM3_PT_LockOverlapping,
        UVPM3_PT_LockGroups,
        UVPM3_PT_Statistics,
        UVPM3_PT_Help
    )



class UVPM3_Mode_Pack(UVPM3_Mode_Main):
    
    MODE_CATEGORY = UVPM3_ModeCategory_Packing
    OPERATOR_IDNAME = UVPM3_OT_Pack.bl_idname


    def operators(self):

        return [
            OperatorMetadata(self.OPERATOR_IDNAME, properties=[('pack_to_others', False)], scale_y=1.4),
            OperatorMetadata(self.OPERATOR_IDNAME, label='Pack To Others', properties=[('pack_to_others', True)])
        ]

    def subpanels(self):

        output = []
        output.append(UVPM3_PT_PackOptions.bl_idname)
        output.append(UVPM3_PT_PixelMargin.bl_idname)
        output.append(UVPM3_PT_Heuristic.bl_idname)
        output.append(UVPM3_PT_LockOverlapping.bl_idname)
        output.append(UVPM3_PT_LockGroups.bl_idname)
        output.append(UVPM3_PT_NonSquarePacking.bl_idname)

        if self.use_main_target_box():
            output.append(UVPM3_PT_TargetBox.bl_idname)

        output.append(UVPM3_PT_IslandRotStep.bl_idname)
        output.append(UVPM3_PT_IslandScaleLimit.bl_idname)
        output.append(UVPM3_PT_Statistics.bl_idname)
        output.append(UVPM3_PT_Help.bl_idname)

        return output

    def pre_operation(self):
        
        self.target_boxes = self.get_target_boxes()

    def packing_operation(self):

        return True

    def get_group_method(self):

        return self.scene_props.group_method

    def use_main_target_box(self):

        return True

    def get_main_target_box(self):

        if not self.use_main_target_box():
            return None

        if self.scene_props.custom_target_box_enable:
            return self.scene_props.custom_target_box

        return DEFAULT_TARGET_BOX

    def get_target_boxes(self):

        main_box = self.get_main_target_box()

        if main_box is None:
            return None

        return [main_box]

    def pack_to_others_enabled(self):

        return self.op.pack_to_others

    def send_unselected_islands(self):

        return self.pack_to_others_enabled()

    def get_box_renderer(self):

        if self.target_boxes is None:
            return None

        box_access = BoxArrayRenderAccess()
        if not box_access.init_access(self.target_boxes, CustomTargetBoxAccess.MAIN_TARGET_BOX_COLOR):
            raise RuntimeError('Count not init box renderer')

        return BoxRenderer(self.context, box_access)

    def validate_params(self):
 
        pass
        # if self.grouping_enabled():

        #     if self.get_group_method() == GroupingMethod.SIMILARITY.code:
        #         if self.prefs.pack_to_others_enabled(self.scene_props):
        #             raise RuntimeError("'Pack To Others' is not supported with grouping by similarity")

        #         if not self.scene_props.rotation_enable:
        #             raise RuntimeError("Island rotations must be enabled in order to group by similarity")

        #         if self.scene_props.pre_rotation_disable:
        #             raise RuntimeError("'Pre-Rotation Disable' option must be off in order to group by similarity")

    def send_verts_3d(self):

        return self.prefs.normalize_islands_enabled(self.scene_props)

    def setup_script_params(self):

        self.validate_params()

        script_params = ScriptParams()

        script_params.add_param('precision', self.scene_props.precision)
        script_params.add_param('margin', self.scene_props.margin)

        if self.prefs.pixel_margin_enabled(self.scene_props):
            script_params.add_param('pixel_margin', self.scene_props.pixel_margin)
            script_params.add_param('pixel_margin_tex_size', self.prefs.pixel_margin_tex_size(self.scene_props, self.context))

            if self.prefs.pixel_padding_enabled(self.scene_props):
                script_params.add_param('pixel_padding', self.scene_props.pixel_padding)

        if self.prefs.fixed_scale_enabled(self.scene_props):
            script_params.add_param('fixed_scale', True)
            script_params.add_param('fixed_scale_strategy', int(self.scene_props.fixed_scale_strategy))

        if self.prefs.FEATURE_island_rotation:
            if self.scene_props.rotation_enable:
                rot_step_value = self.scene_props.rotation_step
                
                script_params.add_param('pre_rotation_disable', self.scene_props.pre_rotation_disable)
            else:
                rot_step_value = -1

            script_params.add_param('rotation_step', rot_step_value)

        if self.prefs.heuristic_enabled(self.scene_props):
            script_params.add_param('heuristic_search_time', self.scene_props.heuristic_search_time)
            script_params.add_param('heuristic_max_wait_time', self.scene_props.heuristic_max_wait_time)

            if self.prefs.FEATURE_advanced_heuristic and self.scene_props.advanced_heuristic:
                script_params.add_param('advanced_heuristic', self.scene_props.advanced_heuristic)

        if self.scene_props.lock_overlapping_enable:
            script_params.add_param('lock_overlapping_mode', int(self.scene_props.lock_overlapping_mode))

        script_params.add_param('pack_to_others', self.pack_to_others_enabled())

        if self.prefs.normalize_islands_enabled(self.scene_props):
            script_params.add_param('normalize_islands', True)

        if self.island_rot_step_enabled():
            script_params.add_param('island_rotation_step_enable', True)

        if self.island_scale_limit_enabled():
            script_params.add_param('scale_limit_iparam_name', ScaleLimitIParamInfo.SCRIPT_NAME)

        if self.lock_groups_enabled():
            script_params.add_param('lock_groups_enable', True)
        
        if self.prefs.pack_ratio_enabled(self.scene_props):
            pack_ratio = get_active_image_ratio(self.context)
            script_params.add_param('__pack_ratio', pack_ratio)

        if self.target_boxes is not None:

            script_params.add_param('target_boxes', [box.coords_tuple() for box in self.target_boxes])

        return script_params

    def island_rot_step_enabled(self):
        return self.scene_props.rotation_enable and self.scene_props.island_rot_step_enable

    def island_scale_limit_enabled(self):
        return not self.scene_props.fixed_scale and self.scene_props.island_scale_limit_enable

    def lock_groups_enabled(self):
        return self.scene_props.lock_groups_enable

    def get_iparam_serializers(self):

        output = []

        if self.island_rot_step_enabled():
            output.append(VColorIParamSerializer(RotStepIParamInfo()))

        if self.island_scale_limit_enabled():
            output.append(VColorIParamSerializer(ScaleLimitIParamInfo()))

        if self.lock_groups_enabled():
            output.append(VColorIParamSerializer(LockGroupIParamInfo()))

        return output



class UVPM3_Mode_SingleTile(UVPM3_Mode_Pack):

    MODE_ID = 'pack.single_tile'
    MODE_NAME = 'Single Tile'
    MODE_PRIORITY = 1000
    MODE_HELP_URL_SUFFIX = "30-packing-modes/10-single-tile"

    SCENARIO_ID = 'pack.general'

class UVPM3_Mode_Tiles(UVPM3_Mode_Pack):

    MODE_ID = 'pack.tiles'
    MODE_NAME = 'Tiles'
    MODE_PRIORITY = 2000
    MODE_HELP_URL_SUFFIX = "30-packing-modes/20-tiles"

    SCENARIO_ID = 'pack.general'

    def subpanels(self):
        output = super().subpanels()
        output.append(UVPM3_PT_TileLayout.bl_idname)

        return output

    def get_target_boxes(self):

        tile_grid_shape = None
        if self.scene_props.use_blender_tile_grid:
            try:
                tile_grid_shape = self.context.space_data.uv_editor.tile_grid_shape
            except:
                pass

        if tile_grid_shape is None:
            tile_count_x = self.scene_props.tile_count_x
            tile_count_y = self.scene_props.tile_count_y
        else:
            tile_count_x = tile_grid_shape[0]
            tile_count_y = tile_grid_shape[1]

        main_box = self.get_main_target_box()

        tile_count_total = tile_count_x * tile_count_y
        tiles_in_row = tile_count_x

        output = []
        
        for i in range(tile_count_total):
            output.append(main_box.tile_from_num(i, tiles_in_row))

        return output

    # def setup_script_params(self):
    #     script_params = super().setup_script_params()

    #     tile_grid_shape = None
    #     if self.scene_props.use_blender_tile_grid:
    #         try:
    #             tile_grid_shape = self.context.space_data.uv_editor.tile_grid_shape
    #         except:
    #             pass

    #     if tile_grid_shape is None:
    #         tile_count_x = self.scene_props.tile_count_x
    #         tile_count_y = self.scene_props.tile_count_y
    #     else:
    #         tile_count_x = tile_grid_shape[0]
    #         tile_count_y = tile_grid_shape[1]

    #     script_params.add_param('tile_count_x', tile_count_x)
    #     script_params.add_param('tile_count_y', tile_count_y)

    #     return script_params


class UVPM3_Mode_GroupsToTiles(UVPM3_Mode_Pack):

    MODE_ID = 'pack.groups_to_tiles'
    MODE_NAME = 'Groups To Tiles'
    MODE_PRIORITY = 3000
    MODE_HELP_URL_SUFFIX = "30-packing-modes/30-groups-to-tiles"

    SCENARIO_ID = 'pack.groups_to_tiles'

    def grouping_enabled(self):
        
        return True

    def use_main_target_box(self):

        return False

    def get_box_renderer(self):
        
        box_access = GroupingSchemeRenderAccess()
        box_access.init_access(self.op.g_scheme)

        return BoxRenderer(self.context, box_access)

class UVPM3_Mode_GroupsTogether(UVPM3_Mode_Pack):

    MODE_ID = 'pack.groups_together'
    MODE_NAME = 'Groups Together'
    MODE_PRIORITY = 4000
    MODE_HELP_URL_SUFFIX = "30-packing-modes/40-groups-together"

    SCENARIO_ID = 'pack.groups_together'

    def grouping_enabled(self):
        
        return True

    def groups_together(self):

        return True

    # def setup_script_params(self):
    #     script_params = super().setup_script_params()

    #     script_params.add_param('group_compactness', self.scene_props.group_compactness)
    #     return script_params

