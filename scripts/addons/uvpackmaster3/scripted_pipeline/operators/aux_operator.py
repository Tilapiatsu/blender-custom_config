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


from ...operator import UVPM3_OT_Engine
from ...island_params import SplitOffsetIParamInfo, VColorIParamSerializer
from ...prefs_scripted_utils import ScriptParams


class AuxFinishConditionMixin:

    # def operation_done_finish_condition(self, event):

    #     return not mouse_move_or_wheel_event(event)

    def operation_done_hint(self):

        return ''



class UVPM3_OT_OverlapCheck(AuxFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.overlap_check'
    bl_label = 'Overlap Check'
    bl_description = 'Check wheter selected UV islands overlap each other'

    SCENARIO_ID = 'aux.overlap_check'


class UVPM3_OT_MeasureArea(AuxFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.measure_area'
    bl_label = 'Measure Area'
    bl_description = 'Measure area of selected UV islands'

    SCENARIO_ID = 'aux.measure_area'



class UVPM3_OT_SplitOverlappingGeneric(UVPM3_OT_Engine):

    def get_iparam_serializers(self):

        return [VColorIParamSerializer(SplitOffsetIParamInfo())]

    def setup_script_params(self):

        script_params = ScriptParams()
        script_params.add_param('split_offset_iparam_name', SplitOffsetIParamInfo.SCRIPT_NAME)
        return script_params


class UVPM3_OT_SplitOverlapping(AuxFinishConditionMixin, UVPM3_OT_SplitOverlappingGeneric):

    bl_idname = 'uvpackmaster3.split_overlapping'
    bl_label = 'Split Overlapping Islands'
    bl_description = 'Move all overlapping islands to adjacent tiles'

    SCENARIO_ID = 'aux.split_overlapping'


class UVPM3_OT_UndoIslandSplit(AuxFinishConditionMixin, UVPM3_OT_SplitOverlappingGeneric):

    bl_idname = 'uvpackmaster3.undo_island_split'
    bl_label = 'Undo Island Split'
    bl_description = 'Undo an island split operation'

    SCENARIO_ID = 'aux.undo_island_split'

    def skip_topology_parsing(self):
        return True



class UVPM3_OT_AdjustTdToUnselected(AuxFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.adjust_td_to_unselected'
    bl_label = 'Adjust TD To Unselected'
    bl_description = 'Adjust texel density of selected islands so it is uniform with texel density of unselected islands'

    SCENARIO_ID = 'aux.adjust_td_to_unselected'

    def send_verts_3d(self):
        return True

    def send_unselected_islands(self):
        return True
