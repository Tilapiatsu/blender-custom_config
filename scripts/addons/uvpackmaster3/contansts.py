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

from .enums import UvpmAxis

class PropConstants:

    ROTATION_ENABLE_DEFAULT = True
    PRE_ROTATION_DISABLE_DEFAULT = False

    ROTATION_STEP_MIN = 1
    ROTATION_STEP_MAX = 180
    ROTATION_STEP_DEFAULT = 90

    FLIPPING_ENABLE_DEFAULT = False

    PIXEL_MARGIN_MIN = 1
    PIXEL_MARGIN_MAX = 256
    PIXEL_MARGIN_DEFAULT = 5

    PIXEL_PADDING_MIN = 0
    PIXEL_PADDING_MAX = 256
    PIXEL_PADDING_DEFAULT = 0

    EXTRA_PIXEL_MARGIN_TO_OTHERS_MIN = 0
    EXTRA_PIXEL_MARGIN_TO_OTHERS_MAX = 128
    EXTRA_PIXEL_MARGIN_TO_OTHERS_DEFAULT = 0

    PIXEL_MARGIN_TEX_SIZE_MIN = 16
    PIXEL_MARGIN_TEX_SIZE_MAX = 32768	
    PIXEL_MARGIN_TEX_SIZE_DEFAULT = 1024

    TILES_IN_ROW_DEFAULT = 10
    TILE_COUNT_PER_GROUP_DEFAULT = 1
    LAST_GROUP_COMPLEMENTARY_DEFAULT = False
    GROUP_COMPACTNESS_DEFAULT = 0.0
    
    ORIENT_PRIM_3D_AXIS_DEFAULT = UvpmAxis.Z.code
    ORIENT_PRIM_UV_AXIS_DEFAULT = UvpmAxis.Y.code
    ORIENT_SEC_3D_AXIS_DEFAULT = UvpmAxis.X.code
    ORIENT_SEC_UV_AXIS_DEFAULT = UvpmAxis.X.code

    ORIENT_PRIM_SEC_BIAS_DEFAULT = 80
