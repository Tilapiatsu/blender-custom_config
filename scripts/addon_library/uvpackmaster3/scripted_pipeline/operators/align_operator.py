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


from ...operator import UVPM3_OT_Engine, ModeIdAttributeMixin


class UVPM3_OT_AlignGeneric(UVPM3_OT_Engine):

    def split_offset_enabled(self):
        return False


class UVPM3_OT_SelectSimilar(UVPM3_OT_AlignGeneric, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.select_similar'
    bl_label = 'Select Similar'
    bl_description = "From all unselected islands, selects all islands which have similar shape to at least one island which is currently selected. For more info regarding similarity detection click the help button"

    SCENARIO_ID = 'align.select_similar'

    def send_unselected_islands(self):
        return True


class UVPM3_OT_AlignSimilar(UVPM3_OT_AlignGeneric, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.align_similar'
    bl_label = 'Align Similar (Stack)'
    bl_description = "Align the selected islands, so islands which are similar are stacked on the top of each other. For more info regarding similarity detection click the help button"

    SCENARIO_ID = 'align.align_similar'


class UVPM3_OT_SplitOverlappingGeneric(UVPM3_OT_AlignGeneric):

    def split_offset_enabled(self):
        return True

    def operation_done_hint(self):
        return ''


class UVPM3_OT_SplitOverlapping(UVPM3_OT_SplitOverlappingGeneric, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.split_overlapping'
    bl_label = 'Split Overlapping Islands'
    bl_description = 'Methodically move overlapping islands to adjacent tiles (in the +X axis direction), so that no selected islands are overlapping each other after the operation is done'

    SCENARIO_ID = 'align.split_overlapping'


class UVPM3_OT_UndoIslandSplit(UVPM3_OT_SplitOverlappingGeneric, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.undo_island_split'
    bl_label = 'Undo Island Split'
    bl_description = 'Undo the last island split operation - move all selected islands to their original locations before split. WARNING: the operation only process currently selected islands so in order to move an island to its original location, you have to make sure the island is selected when an Undo operation is run'

    SCENARIO_ID = 'align.undo_island_split'

    def skip_topology_parsing(self):
        return True
