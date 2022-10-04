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


from ...mode import ModeType, UVPM3_Mode_Generic
from ..operators.aux_operator import (
        UVPM3_OT_OverlapCheck,
        UVPM3_OT_MeasureArea,
        UVPM3_OT_AdjustTdToUnselected
    )


class UVPM3_Mode_Aux(UVPM3_Mode_Generic):
    
    MODE_TYPE = ModeType.AUX


class UVPM3_Mode_OverlapCheck(UVPM3_Mode_Aux):

    MODE_ID = 'aux.overlap_check'
    MODE_NAME = 'Overlap Check'
    MODE_PRIORITY = 1000

    OPERATOR_IDNAME = UVPM3_OT_OverlapCheck.bl_idname


class UVPM3_Mode_MeasureArea(UVPM3_Mode_Aux):

    MODE_ID = 'aux.measure_area'
    MODE_NAME = 'Measure Area'
    MODE_PRIORITY = 2000

    OPERATOR_IDNAME = UVPM3_OT_MeasureArea.bl_idname


class UVPM3_Mode_AdjustTdToUnselected(UVPM3_Mode_Aux):

    MODE_ID = 'aux.andjust_td_to_unselected'
    MODE_NAME = UVPM3_OT_AdjustTdToUnselected.bl_label
    MODE_PRIORITY = 5000

    OPERATOR_IDNAME = UVPM3_OT_AdjustTdToUnselected.bl_idname
