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


from .labels import UvpLabels
from .blend import get_prefs

# TODO: rename this file to types.py


class OpFinishedException(Exception):
    pass

class OpCancelledException(Exception):
    pass

class OpAbortedException(Exception):
    pass


class UvPackerOpcode:
    REPORT_VERSION = 0
    PACK = 1
    OVERLAP_CHECK = 2
    MEASURE_AREA = 3
    VALIDATE_UVS = 4
    SELECT_SIMILAR = 5
    ALIGN_SIMILAR = 6
    GET_ISLANDS_METADATA = 7

class UvPackMessageCode:
    PROGRESS_REPORT = 0
    INVALID_ISLANDS = 1
    VERSION = 2
    ISLAND_FLAGS = 3
    PACK_SOLUTION = 4
    AREA = 5
    INVALID_FACES = 6
    SIMILAR_ISLANDS = 7
    BENCHMARK = 8
    ISLANDS = 9
    ISLANDS_METADATA = 10

class UvPackerIslandFlags:
    OVERLAPS = 1
    OUTSIDE_TARGET_BOX = 2

class UvPackerFeatureCode:
    DEMO = 0
    ISLAND_ROTATION = 1
    OVERLAP_CHECK = 2
    PACKING_DEPTH = 3
    HEURISTIC_SEARCH = 4
    PACK_RATIO = 5
    PACK_TO_OTHERS = 6
    GROUPING = 7
    LOCK_OVERLAPPING = 8
    ADVANCED_HEURISTIC = 9
    SELF_INTERSECT_PROCESSING = 10
    VALIDATION = 11
    MULTI_DEVICE_PACK = 12
    TARGET_BOX = 13
    ISLAND_ROTATION_STEP = 14
    PACK_TO_TILES = 15

class UvPackerErrorCode:
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ISLANDS = 2
    NO_SPACE = 3
    NO_VALID_STATIC_ISLAND = 4
    MAX_GROUP_COUNT_EXCEEDED = 5
    CANCELLED = 6
    PRE_VALIDATION_FAILED = 7
    DEVICE_NOT_SUPPORTED = 8
    DEVICE_DOESNT_SUPPORT_GROUPS_TOGETHER = 9
    NO_UVS = 10
    NO_SELECTED_UVS = 11

class UvPackingPhaseCode:
    INITIALIZATION = 0
    TOPOLOGY_ANALYSIS = 1
    PIXEL_MARGIN_ADJUSTMENT = 2
    PACKING = 3
    AREA_MEASUREMENT = 4
    OVERLAP_CHECK = 5
    RENDER_PRESENTATION = 6
    TOPOLOGY_VALIDATION = 7
    VALIDATION = 8
    SIMILAR_SELECTION = 9
    SIMILAR_ALIGNING = 10
    DONE = 11

class UvTopoAnalysisLevel:
    SIMPLE = 0
    EXTENDED = 1
    PROCESS_SELF_INTERSECT = 2
    FORCE_EXTENDED = 3


class EnumValue:

    @classmethod
    def to_blend_enums(cls, enum_values):

        prefs = get_prefs()
        items = []

        for enum_val in enum_values:
            supported = (enum_val.req_feature == '') or getattr(prefs, 'FEATURE_' + enum_val.req_feature)

            items.append(enum_val.to_blend_enum(supported))

        return items

    def __init__(self, code, name, desc='', req_feature=''):
        self.code = code
        self.name = name
        self.desc = desc
        self.req_feature = req_feature

    def to_blend_enum(self, supported=True):

        if supported:
            name =  self.name
            icon = 'NONE'
        else:
            name = self.name + ' ' + UvpLabels.FEATURE_NOT_SUPPORTED_MSG
            icon = UvpLabels.FEATURE_NOT_SUPPORTED_ICON

        return (self.code, name, self.desc, icon, int(self.code))


class UvPackingModeEntry:

    def __init__(self, code, name, desc, req_feature, supports_heuristic, supports_pack_to_others, supports_fixed_scale):
        self.code = code
        self.name = name
        self.req_feature = req_feature
        self.supports_heuristic = supports_heuristic
        self.supports_pack_to_others = supports_pack_to_others
        self.supports_fixed_scale = supports_fixed_scale
        self.enum_val = EnumValue(code, name, desc, req_feature)

class UvPackingMode:

    @classmethod
    def to_blend_enums(cls):

        enum_values = \
            (cls.SINGLE_TILE.enum_val,
             cls.TILES.enum_val,
             cls.GROUPS_TOGETHER.enum_val,
             cls.GROUPS_TO_TILES.enum_val)

        return EnumValue.to_blend_enums(enum_values)

    @classmethod
    def get_mode(cls, code):

        for mode in cls.MODES:
            if mode.code == code:
                return mode

        raise RuntimeError('Unexpected packing mode provided')

    SINGLE_TILE = UvPackingModeEntry(\
                    '0',
                    UvpLabels.PACK_MODE_SINGLE_TILE_NAME,
                    UvpLabels.PACK_MODE_SINGLE_TILE_DESC,
                    '',
                    supports_heuristic=True,
                    supports_pack_to_others=True,
                    supports_fixed_scale=True)

    TILES = UvPackingModeEntry(\
                    '1',
                    UvpLabels.PACK_MODE_TILES_NAME,
                    UvpLabels.PACK_MODE_TILES_DESC,
                    'pack_to_tiles',
                    supports_heuristic=True,
                    supports_pack_to_others=True,
                    supports_fixed_scale=True)

    GROUPS_TOGETHER = UvPackingModeEntry(\
                    '2',
                    UvpLabels.PACK_MODE_GROUPS_TOGETHER_NAME,
                    UvpLabels.PACK_MODE_GROUPS_TOGETHER_DESC,
                    'grouping',
                    supports_heuristic=True,
                    supports_pack_to_others=True,
                    supports_fixed_scale=True)

    GROUPS_TO_TILES = UvPackingModeEntry(\
                    '3',
                    UvpLabels.PACK_MODE_GROUPS_TO_TILES_NAME,
                    UvpLabels.PACK_MODE_GROUPS_TO_TILES_DESC,
                    'grouping',
                    supports_heuristic=True,
                    supports_pack_to_others=True,
                    supports_fixed_scale=True)

    MODES = [SINGLE_TILE, TILES, GROUPS_TOGETHER, GROUPS_TO_TILES]


class UvGroupingMode_Legacy:
    DISABLED = EnumValue('0', '', '')
    PACK_TOGETHER = EnumValue('1', '', '')
    PACK_TO_TILES = EnumValue('2', '', '')

class UvGroupingMethod:
    MATERIAL = EnumValue('0', 'Material', UvpLabels.GROUP_METHOD_MATERIAL_DESC)
    SIMILARITY = EnumValue('1', 'Similarity', UvpLabels.GROUP_METHOD_SIMILARITY_DESC)
    MESH = EnumValue('2', 'Mesh Parts', UvpLabels.GROUP_METHOD_MESH_DESC)
    OBJECT = EnumValue('3', 'Object', UvpLabels.GROUP_METHOD_OBJECT_DESC)
    MANUAL = EnumValue('4', 'Manual', UvpLabels.GROUP_METHOD_MANUAL_DESC)
    TILE = EnumValue('5', 'UDIM Tile', UvpLabels.GROUP_METHOD_TILE_DESC)

class UvFixedScaleStrategy:
    BOTTOM_TOP = EnumValue('0', 'Bottom-Top')
    LEFT_RIGHT = EnumValue('1', 'Left-Right')
    SQUARE = EnumValue('2', 'Square')

    @classmethod
    def to_blend_enums(cls):
        return (cls.BOTTOM_TOP.to_blend_enum(), cls.LEFT_RIGHT.to_blend_enum(), cls.SQUARE.to_blend_enum())

class UvPixelMarginMethod:
    ADJUSTMENT_TIME = EnumValue('0', 'Adjustment Time (Recommended)', UvpLabels.PIXEL_MARGIN_METHOD_ADJUSTMENT_TIME_DESC)
    ITERATIVE = EnumValue('1', 'Iterative', UvpLabels.PIXEL_MARGIN_METHOD_ITERATIVE_DESC)

class UvGroupingMethodUvp:
    DISABLED = 0
    EXTERNAL = 1
    SIMILARITY = 2

class UvLockOverlappingMode:
    DISABLED = EnumValue('0', 'Disabled', UvpLabels.LOCK_OVERLAPPING_MODE_DISABLED_DESC)
    ANY_PART = EnumValue('1', 'Any Part', UvpLabels.LOCK_OVERLAPPING_MODE_ANY_PART_DESC)
    EXACT = EnumValue('2', 'Exact', UvpLabels.LOCK_OVERLAPPING_MODE_EXACT_DESC)

class UvMapSerializationFlags:
    CONTAINS_FLAGS = 1
    CONTAINS_GROUPS = 2
    CONTAINS_ROT_STEP = 4
    CONTAINS_VERTS_3D = 8
    CONTAINS_LOCK_GROUPS = 16

class UvFaceInputFlags:
    SELECTED = 1

class UvDeviceFlags:
    SUPPORTED = 1
    SUPPORTS_GROUPS_TOGETHER = 2

class UvIslandIntParams:
    GROUP = 0
    ROTATION_STEP = 1
    LOCK_GROUP = 2
    COUNT = 3

class UvInvalidIslandCode:
    TOPOLOGY = 0
    INT_PARAM = 1


