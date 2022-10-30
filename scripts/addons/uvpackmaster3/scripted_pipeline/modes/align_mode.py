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

from ...enums import UvpmSimilarityMode, UvpmAxis
from ...prefs_scripted_utils import ScriptParams
from ...mode import UVPM3_Mode_Main, UVPM3_ModeCategory_Miscellaneous, OperatorMetadata, OperatorMetadataSeparator
from ...island_params import AlignPriorityIParamInfo, SplitOffsetIParamInfo, VColorIParamSerializer
from ..operators.align_operator import UVPM3_OT_SelectSimilar, UVPM3_OT_AlignSimilar, UVPM3_OT_SplitOverlapping, UVPM3_OT_UndoIslandSplit
from ..panels.align_panels import UVPM3_PT_SimilarityOptions, UVPM3_PT_AlignPriority



class UVPM3_Mode_Align(UVPM3_Mode_Main):

    MODE_ID = 'aligning_tools'
    MODE_NAME = 'Aligning Tools'
    MODE_PRIORITY = 10000
    MODE_HELP_URL_SUFFIX = "40-miscellaneous-modes/10-aligning-tools"

    MODE_CATEGORY = UVPM3_ModeCategory_Miscellaneous

    VERTEX_BASED_MODE_PRECISION = 500
    VERTEX_BASED_MODE_THRESHOLD = 1.0


    def subpanels(self):

        return [UVPM3_PT_SimilarityOptions.bl_idname, UVPM3_PT_AlignPriority.bl_idname]

    def setup_script_params(self):

        if UvpmSimilarityMode.is_vertex_based(self.scene_props.simi_mode):
            precision = self.VERTEX_BASED_MODE_PRECISION
            threshold = self.VERTEX_BASED_MODE_THRESHOLD
        else:
            precision = self.scene_props.precision
            threshold = self.scene_props.simi_threshold

        script_params = ScriptParams()
        script_params.add_param('mode', self.scene_props.simi_mode)
        script_params.add_param('precision', precision)
        script_params.add_param('threshold', threshold)
        script_params.add_param('flipping_enable', self.scene_props.flipping_enable)
        script_params.add_param('adjust_scale', self.scene_props.simi_adjust_scale)
        # script_params.add_param('match_3d_orientation', self.scene_props.simi_match_3d_orientation)
        script_params.add_param('match_3d_axis', self.scene_props.simi_match_3d_axis)
        script_params.add_param('correct_vertices', self.scene_props.simi_correct_vertices)
        script_params.add_param('vertex_threshold', self.scene_props.simi_vertex_threshold)

        if self.align_priority_enabled():
            script_params.add_param('align_priority_iparam_name', AlignPriorityIParamInfo.SCRIPT_NAME)

        if self.split_offset_enabled():
            script_params.add_param('split_offset_iparam_name', SplitOffsetIParamInfo.SCRIPT_NAME)

        # if self.prefs.pack_ratio_enabled(self.scene_props):
        #     self.pack_ratio = get_active_image_ratio(self.p_context.context)
        #     engine_args += ['-q', str(self.pack_ratio)]

        return script_params

    def align_priority_enabled(self):
        return self.scene_props.align_priority_enable

    def split_offset_enabled(self):
        return self.op.split_offset_enabled()

    def send_verts_3d(self):
        return self.scene_props.simi_match_3d_axis != UvpmAxis.NONE.code

    def verts_3d_space(self):
        return self.scene_props.simi_match_3d_axis_space

    def get_iparam_serializers(self):

        output = []

        if self.align_priority_enabled():
            output.append(VColorIParamSerializer(AlignPriorityIParamInfo()))

        if self.split_offset_enabled():
            output.append(VColorIParamSerializer(SplitOffsetIParamInfo()))

        return output

    def operators(self):
        return [
            OperatorMetadata(UVPM3_OT_SelectSimilar.bl_idname),
            OperatorMetadata(UVPM3_OT_AlignSimilar.bl_idname),
            OperatorMetadataSeparator(),
            OperatorMetadata(UVPM3_OT_SplitOverlapping.bl_idname),
            OperatorMetadata(UVPM3_OT_UndoIslandSplit.bl_idname)
        ]
