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
from ...labels import Labels
from ...enums import *
from ...utils import *


from bpy.props import BoolProperty
from mathutils import Vector


class UVPM3_OT_Pack(UVPM3_OT_Engine, ModeIdAttributeMixin):

    bl_idname = 'uvpackmaster3.pack'
    bl_label = 'Pack'
    bl_description = 'Pack selected UV islands'

    pack_to_others : BoolProperty(
        name=Labels.PACK_TO_OTHERS_NAME,
        description=Labels.PACK_TO_OTHERS_DESC,
        default=False)
