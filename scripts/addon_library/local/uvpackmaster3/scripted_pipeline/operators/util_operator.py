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


class UtilFinishConditionMixin:
    
    # def operation_done_finish_condition(self, event):

    #     return not mouse_move_or_wheel_event(event)

    def operation_done_hint(self):

        return ''



class UVPM3_OT_OverlapCheck(UtilFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.overlap_check'
    bl_label = 'Overlap Check'
    bl_description = "Check for overlapping UV islands among all selected islands. WARNING: this operation works on a per-island basis (reports whether two distinct UV islands overlap each other) - it will NOT report two overlapping UV faces belonging to the same island"

    SCENARIO_ID = 'util.overlap_check'


class UVPM3_OT_MeasureArea(UtilFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.measure_area'
    bl_label = 'Measure Area'
    bl_description = 'Measure area of selected UV islands'

    SCENARIO_ID = 'util.measure_area'


class UVPM3_OT_AdjustTdToUnselected(UtilFinishConditionMixin, UVPM3_OT_Engine):

    bl_idname = 'uvpackmaster3.adjust_td_to_unselected'
    bl_label = 'Adjust TD To Unselected'
    bl_description = 'Adjust texel density of selected islands so it is uniform with texel density of unselected islands'

    SCENARIO_ID = 'util.adjust_td_to_unselected'

    def skip_topology_parsing(self):
        return True

    def send_verts_3d(self):
        return True

    def send_unselected_islands(self):
        return True
