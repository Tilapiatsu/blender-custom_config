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

from ...mode import UVPM3_Mode_Main, UVPM3_ModeCategory_Miscellaneous


class UVPM3_Mode_Other(UVPM3_Mode_Main):

    MODE_ID = 'other_tools'
    MODE_NAME = 'Other Tools'
    MODE_PRIORITY = 12000
    MODE_HELP_URL_SUFFIX = "40-miscellaneous-modes/20-other-tools"

    MODE_CATEGORY = UVPM3_ModeCategory_Miscellaneous

    def subpanels(self):
        from ..panels.other_panels import UVPM3_PT_OrientTo3dSpace
        return [UVPM3_PT_OrientTo3dSpace.bl_idname]

    # def operators(self):
    #     return []
