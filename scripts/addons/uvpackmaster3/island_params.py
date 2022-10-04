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


from .connection import encode_string, decode_string, force_read_int
from .enums import *
from .utils import rgb_to_rgba
from .pack_context import PackContext



import struct


class IParamInfo:

    PARAM_TYPE = int
    PARAM_TYPE_MARK = 'i'
    TEXT_TYPE = PARAM_TYPE
    VALUE_PROP_NAME = None
    
    DEFAULT_VALUE_TEXT = None
    TEXT_SUFFIX = None

    VCOLOR_CHANNEL_NAME_PREFIX = '__uvpm3_v2_'
    # VALUE_TO_VCOLOR = (lambda self, val: (val, val, val, 1.0))
    VCOLOR_CHANNEL_COUNT = 3
    VCOLOR_CHANNEL_VALUE_COUNT = 256
    VCOLOR_CHANNEL_MAX_VALUE = VCOLOR_CHANNEL_VALUE_COUNT-1

    INT_TO_VCOLOR_CH = (lambda self, input: float(input) / (IParamInfo.VCOLOR_CHANNEL_MAX_VALUE))
    VCOLOR_CH_TO_INT = (lambda self, input: int(input * (IParamInfo.VCOLOR_CHANNEL_MAX_VALUE)))

    INDEX = -1

    def __init__(self, script_name, label, min_value, max_value, default_value=None):
        self.label = label
        self.script_name = script_name
        self.min_value = self.PARAM_TYPE(min_value)
        self.max_value = self.PARAM_TYPE(max_value)
        self.default_value = self.min_value if default_value is None else self.PARAM_TYPE(default_value)
    
    def get_vcolor_chname(self):
        return self.VCOLOR_CHANNEL_NAME_PREFIX + self.script_name

    def vcolor_to_param_allchannels(self, vcolor):

        zero_based_value = self.VCOLOR_CH_TO_INT(vcolor[0])

        if vcolor[1] > 0.0:
            multiplier = self.VCOLOR_CHANNEL_VALUE_COUNT
            for i in range(1, self.VCOLOR_CHANNEL_COUNT):
                zero_based_value += multiplier * self.VCOLOR_CH_TO_INT(vcolor[i])
                multiplier *= self.VCOLOR_CHANNEL_VALUE_COUNT

        param_value = zero_based_value + self.min_value

        if param_value < self.min_value or param_value > self.max_value:
            param_value = self.default_value

        return param_value

    
    def vcolor_to_param(self, vcolor):
        return self.vcolor_to_param_allchannels(vcolor)

    def param_to_vcolor_allchannels(self, iparam_value):
        assert(iparam_value >= self.min_value)
        zero_based_value = iparam_value - self.min_value

        ch_values = [0.0] * self.VCOLOR_CHANNEL_COUNT

        for i in range(self.VCOLOR_CHANNEL_COUNT):
            ch_values[i] = self.INT_TO_VCOLOR_CH(zero_based_value % self.VCOLOR_CHANNEL_VALUE_COUNT)
            zero_based_value //= self.VCOLOR_CHANNEL_VALUE_COUNT

            if zero_based_value == 0:
                break

        if zero_based_value > 0:
            raise RuntimeError('Too large island param value provided')

        return (ch_values[0], ch_values[1], ch_values[2], 1.0)

    
    def param_to_vcolor(self, iparam_value):
        return self.param_to_vcolor_allchannels(iparam_value)

    def index(self):

        if self.INDEX < 0:
            raise ValueError()

        return self.INDEX
    
    def get_default_vcolor(self):
        return self.param_to_vcolor(self.default_value)

    
    def param_to_text(self, value):
        if self.DEFAULT_VALUE_TEXT is not None and (value == self.default_value):
            return self.DEFAULT_VALUE_TEXT

        return str(self.TEXT_TYPE(value)) + (self.TEXT_SUFFIX if self.TEXT_SUFFIX is not None else '')

    
    def param_to_color(self, value):
        return (1,1,1,1)

    
    def serialize(self):
        output = encode_string(self.script_name)
        output += encode_string(self.label)
        output += struct.pack(self.PARAM_TYPE_MARK, self.PARAM_TYPE(self.min_value))
        output += struct.pack(self.PARAM_TYPE_MARK, self.PARAM_TYPE(self.max_value))
        output += struct.pack(self.PARAM_TYPE_MARK, self.PARAM_TYPE(self.default_value))
        output += struct.pack('i', int(self.INDEX))

        return output

    # @classmethod
    # def deserialize(cls, stream):
    #     iparam_info = IParamInfo(
    #         script_name=decode_string(stream),
    #         label=decode_string(stream),
    #         min_value=force_read_int(stream),
    #         max_value=force_read_int(stream),
    #         default_value=force_read_int(stream))

    #     param_index = force_read_int(stream)
    #     return iparam_info, param_index


class StaticIParamInfo(IParamInfo):

    def __init__(self):
        default_value = self.DEFAULT_VALUE if hasattr(self, 'DEFAULT_VALUE') else None

        super().__init__(
            script_name=self.SCRIPT_NAME,
            label=self.LABEL,
            min_value=self.MIN_VALUE,
            max_value=self.MAX_VALUE,
            default_value=default_value
        )


class GroupIParamInfoGeneric(StaticIParamInfo):

    TEXT_TYPE = int
    GROUP_COLORS = [
		(0.0,   0.0,    1.0),
        (1.0,   1.0,    0.0),
        (0.0,   1.0,    1.0),
        (0.0,   1.0,    0.0),
        (1.0,   0.25,   0.0),
        (1.0,   0.0,    0.25),
        (0.25,  0.0,    1.0),
        (0.0,   0.25,   1.0),
        (1.0,   0.0,    0.0),
        (0.5,   0.0,    0.5),
        (1.0,   0.0,    0.5),
        (1.0,   0.0,    1.0),
        (0.5,   1.0,    0.0),
    ]

    def param_to_color(self, value):
        return rgb_to_rgba(self.GROUP_COLORS[int(value) % len(self.GROUP_COLORS)])


class RotStepIParamInfo(StaticIParamInfo):

    TEXT_TYPE = int
    LABEL = 'Rotation Step'
    SCRIPT_NAME = 'rotation_step'

    USE_GLOBAL_VALUE = -1

    MIN_VALUE = USE_GLOBAL_VALUE
    MAX_VALUE = 180

    DEFAULT_VALUE_TEXT = 'G'
    TEXT_SUFFIX = 'd'
    VALUE_PROP_NAME = 'island_rot_step'
    



class ScaleLimitIParamInfo(StaticIParamInfo):

    TEXT_TYPE = int
    LABEL = 'Scale Limit'
    SCRIPT_NAME = 'scale_limit_v2'

    MIN_SCALE_LIMIT_VALUE = 10
    MAX_SCALE_LIMIT_VALUE = 1000

    MIN_VALUE = MIN_SCALE_LIMIT_VALUE - 1
    MAX_VALUE = MAX_SCALE_LIMIT_VALUE
    
    DEFAULT_VALUE_TEXT = 'N'
    TEXT_SUFFIX = '%'
    VALUE_PROP_NAME = 'island_scale_limit'
    
    


class LockGroupIParamInfo(GroupIParamInfoGeneric):

    TEXT_TYPE = int
    LABEL = 'Lock Group'
    SCRIPT_NAME = 'lock_group'

    MIN_VALUE = 0
    MAX_VALUE = 100
    DEFAULT_VALUE = MIN_VALUE
    DEFAULT_VALUE_TEXT = 'N'

    VALUE_PROP_NAME = 'lock_group_num'

    

class AlignPriorityIParamInfo(GroupIParamInfoGeneric):

    TEXT_TYPE = int
    LABEL = 'Align Priority'
    SCRIPT_NAME = 'align_priority'

    MIN_VALUE = 0
    MAX_VALUE = 100
    DEFAULT_VALUE = MIN_VALUE
    
    VALUE_PROP_NAME = 'align_priority'



class SplitOffsetIParamInfo(StaticIParamInfo):

    TEXT_TYPE = int
    LABEL = 'Split Offset'
    SCRIPT_NAME = 'split_offset'

    MIN_VALUE = -1
    MAX_VALUE = 10000
    DEFAULT_VALUE = MIN_VALUE



class IParamError(RuntimeError):

    def __init__(self, str):
        super().__init__(str)



class IParamSerializer:

    def __init__(self, iparam_info):

        self.iparam_info = iparam_info
        self.iparam_values = []

    def init_context(self, p_context):

        p_context.register_iparam(self.iparam_info)

class VColorIParamSerializer(IParamSerializer):

    def init_context(self, p_context):
        super().init_context(p_context)
        self.vcolor_layers = []

        for p_obj in p_context.p_objects:
            self.vcolor_layers.append(p_obj.get_or_create_vcolor_layer(self.iparam_info))

    def serialize_iparam(self, p_obj_idx, p_obj, face):
        
        self.iparam_values.append(PackContext.load_iparam(self.iparam_info, self.vcolor_layers[p_obj_idx], face))
