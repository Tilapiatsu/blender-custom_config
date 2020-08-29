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


from .enums import *
from .prefs import is_blender28


class IslandParamInfo:

    VCOLOR_CHNAME_PREFIX = '__uvp2_'
    VALUE_TO_VCOLOR = (lambda val: (val, val, val, 1.0)) if is_blender28() else (lambda val: (val, val, val))

    MAX_PERCHANNEL_VALUE = 255
    INT_TO_VCOLOR_CH = (lambda input: float(input) / IslandParamInfo.MAX_PERCHANNEL_VALUE)
    VCOLOR_CH_TO_INT = (lambda input: int(input * IslandParamInfo.MAX_PERCHANNEL_VALUE))

    @classmethod
    def get_vcolor_chname(cls):
        return cls.VCOLOR_CHNAME_PREFIX + cls.VCOLOR_CHNAME_SUFFIX

    @classmethod
    def get_param_info_array(cls):

        param_array = [None] * UvIslandIntParams.COUNT
        param_array[UvIslandIntParams.GROUP] = GroupIslandParamInfo()
        param_array[UvIslandIntParams.ROTATION_STEP] = RotStepIslandParamInfo()

        return param_array

    @classmethod
    def vcolor_to_param_allchannels(cls, vcolor):

        zero_based_value = 0
        multiplier = 1

        for i in range(3):
            zero_based_value += multiplier * cls.VCOLOR_CH_TO_INT(vcolor[i])
            multiplier *= cls.MAX_PERCHANNEL_VALUE

        return zero_based_value + cls.MIN_VALUE

    @classmethod
    def vcolor_to_param(cls, vcolor):
        if cls.ALL_CHANNELS:
            return cls.vcolor_to_param_allchannels(vcolor)

        f_value = vcolor[0]
        return int(round((cls.MAX_VALUE - cls.MIN_VALUE) * f_value + cls.MIN_VALUE))

    @classmethod
    def param_to_vcolor_allchannels(cls, param_value):
        zero_based_value = param_value - cls.MIN_VALUE

        ch_values = [cls.INT_TO_VCOLOR_CH(0)] * 3

        for i in range(3):
            ch_values[i] = cls.INT_TO_VCOLOR_CH(zero_based_value % cls.MAX_PERCHANNEL_VALUE)
            zero_based_value //= cls.MAX_PERCHANNEL_VALUE

            if zero_based_value == 0:
                break

        if zero_based_value > 0:
            raise RuntimeError('Too large island param provided')

        return (ch_values[0], ch_values[1], ch_values[2], 1.0)

    @classmethod
    def param_to_vcolor(cls, param_value):
        if cls.ALL_CHANNELS:
            return cls.param_to_vcolor_allchannels(param_value)

        value = (float(param_value) - cls.MIN_VALUE) / (cls.MAX_VALUE - cls.MIN_VALUE)
        return cls.VALUE_TO_VCOLOR(value)

    @classmethod
    def get_default_vcolor(cls):
        return cls.param_to_vcolor(cls.DEFAULT_VALUE)

    @classmethod
    def param_to_text(cls, value):
        return str(value)

    @classmethod
    def param_to_color(cls, value):
        return (1,1,1,1)


class GroupIslandParamInfo(IslandParamInfo):

    NAME = 'Group'
    VCOLOR_CHNAME_SUFFIX = 'group'
    ALL_CHANNELS = False

    MIN_VALUE = 0
    MAX_VALUE = 100
    DEFAULT_VALUE = MIN_VALUE
    
    PARAM_IDX = UvIslandIntParams.GROUP
    PROP_NAME = 'manual_group_num'
    
    GROUP_COLORS = [
		(0.0, 0.0, 1.0, 1.0),
        (1.0, 1.0, 0.0, 1.0),
        (0.0, 1.0, 1.0, 1.0),
        (0.0, 1.0, 0.0, 1.0),
        (1.0, 0.25, 0.0, 1.0),
        (1.0, 0.0, 0.25, 1.0),
        (0.25, 0.0, 1.0, 1.0),
        (0.0, 0.25, 1.0, 1.0),
        (1.0, 0.0, 0.0, 1.0),
        (0.5, 0.0, 0.5, 1.0),
        (1.0, 0.0, 0.5, 1.0),
        (1.0, 0.0, 1.0, 1.0),
        (0.5, 1.0, 0.0, 1.0),
    ]

    @classmethod
    def param_to_color(cls, value):
        return cls.GROUP_COLORS[value % len(cls.GROUP_COLORS)]


class RotStepIslandParamInfo(IslandParamInfo):

    NAME = 'Rotation Step'
    VCOLOR_CHNAME_SUFFIX = 'rot_step'
    USE_GLOBAL_VALUE = -1
    ALL_CHANNELS = False

    MIN_VALUE = -1
    MAX_VALUE = 180
    DEFAULT_VALUE = USE_GLOBAL_VALUE
    
    PARAM_IDX = UvIslandIntParams.ROTATION_STEP
    PROP_NAME = 'island_rot_step'

    @classmethod
    def param_to_text(cls, value):
        if value == cls.USE_GLOBAL_VALUE:
            return 'G'

        return str(value)


class SplitOffsetParamInfo(IslandParamInfo):

    NAME = 'Split Offset'
    VCOLOR_CHNAME_SUFFIX = 'split_offset'
    ALL_CHANNELS = True

    MIN_VALUE = -1
    MAX_VALUE = 10000
    DEFAULT_VALUE = MIN_VALUE
    INVALID_VALUE = MIN_VALUE

    PARAM_IDX = None
    PROP_NAME = None



class IslandParamError(RuntimeError):

    def __init__(self, str):
        super().__init__(str)