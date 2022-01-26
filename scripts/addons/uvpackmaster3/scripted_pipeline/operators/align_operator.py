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



class UVPM3_OT_SelectSimilar(UVPM3_OT_Engine, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.select_similar'
    bl_label = 'Select Similar'
    bl_description = "Selects all islands which have similar shape to islands which are already selected. For more info regarding similarity detection click the help button"

    SCENARIO_ID = 'align.select_similar'

    def send_unselected_islands(self):

        return True


class UVPM3_OT_AlignSimilar(UVPM3_OT_Engine, ModeIdAttributeMixin):

    SCENARIO_ID = 'align.align_similar'

    bl_idname = 'uvpackmaster3.align_similar'
    bl_label = 'Align Similar (Stack)'
    bl_description = "Align the selected islands, so islands which are similar are stacked on the top of each other. For more info regarding similarity detection click the help button"

