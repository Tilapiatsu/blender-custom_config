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


import bpy
from .labels import Labels
from .blend import get_prefs

# TODO: rename this file to types.py


class OpFinishedException(Exception):
    pass

class OpAbortedException(Exception):
    pass


class EnumValue:

    @classmethod
    def to_blend_items(cls, enum_values):

        prefs = get_prefs()
        items = []

        for enum_val in enum_values:
            supported = (enum_val.req_feature == '') or getattr(prefs, 'FEATURE_' + enum_val.req_feature)

            items.append(enum_val.to_blend_item(supported))

        return items

    def __init__(self, code, name, desc='', req_feature=''):
        self.code = code
        self.name = name
        self.desc = desc
        self.req_feature = req_feature

    def to_blend_item(self, supported=True):

        if supported:
            name =  self.name
            icon = 'NONE'
        else:
            name = self.name + ' ' + Labels.FEATURE_NOT_SUPPORTED_MSG
            icon = Labels.FEATURE_NOT_SUPPORTED_ICON

        return (self.code, name, self.desc, icon, int(self.code))


class UvpmOpcode:
    REPORT_VERSION = 0
    EXECUTE_SCENARIO = 1


class UvpmMessageCode:
    PHASE = 0
    VERSION = 1
    BENCHMARK = 2
    ISLANDS = 3
    OUT_ISLANDS = 4
    LOG = 5

class UvpmOutIslandsSerializationFlags:
    CONTAINS_TRANSFORM = 1
    CONTAINS_IPARAMS = 2
    CONTAINS_FLAGS = 4
    CONTAINS_VERTICES = 8

class UvpmIslandFlags:
    OVERLAPS = 1
    OUTSIDE_TARGET_BOX = 2
    ALIGNED = 4
    SELECTED = 8

class UvpmFeatureCode:
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

class UvpmLogType:
    STATUS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    HINT = 4

class UvpmRetCode:
    NOT_SET = -1
    SUCCESS = 0
    FATAL_ERROR = 1
    NO_SPACE = 2
    CANCELLED = 3
    INVALID_ISLANDS = 4
    NO_SIUTABLE_DEVICE = 5
    NO_UVS = 6
    INVALID_INPUT = 7
    WARNING = 8

class UvpmPhaseCode:
    RUNNING = 0
    STOPPED = 1
    DONE = 2



class UvpmFixedScaleStrategy:
    BOTTOM_TOP = EnumValue('0', 'Bottom-Top')
    LEFT_RIGHT = EnumValue('1', 'Left-Right')
    SQUARE = EnumValue('2', 'Square')

    @classmethod
    def to_blend_items(cls):
        return (cls.BOTTOM_TOP.to_blend_item(), cls.LEFT_RIGHT.to_blend_item(), cls.SQUARE.to_blend_item())


class UvpmLockOverlappingMode:
    DISABLED = EnumValue('0', 'Disabled', 'Not used')
    ANY_PART = EnumValue('1', 'Any Part', Labels.LOCK_OVERLAPPING_MODE_ANY_PART_DESC)
    EXACT = EnumValue('2', 'Exact', Labels.LOCK_OVERLAPPING_MODE_EXACT_DESC)

    @classmethod
    def to_blend_items(cls):
        return (cls.ANY_PART.to_blend_item(), cls.EXACT.to_blend_item())

class UvpmMapSerializationFlags:
    CONTAINS_FLAGS = 1
    CONTAINS_VERTS_3D = 2

class UvpmFaceInputFlags:
    SELECTED = 1

class UvpmDeviceFlags:
    SUPPORTED = 1
    SUPPORTS_GROUPS_TOGETHER = 2

class UvpmIslandIntParams:
    MAX_COUNT = 16


class OperationStatus:
    ERROR = 0
    WARNING = 1
    CORRECT = 2


class RetCodeMetadata:

    def __init__(self, op_status):
        self.op_status = op_status


RETCODE_METADATA = {
    UvpmRetCode.NOT_SET : RetCodeMetadata(
        op_status=None
    ),
    UvpmRetCode.SUCCESS : RetCodeMetadata(
        op_status=OperationStatus.CORRECT
    ),
    UvpmRetCode.FATAL_ERROR : RetCodeMetadata(
        op_status=OperationStatus.ERROR
    ),
    UvpmRetCode.NO_SPACE : RetCodeMetadata(
        op_status=OperationStatus.WARNING
    ),
    UvpmRetCode.CANCELLED : RetCodeMetadata(
        op_status=OperationStatus.CORRECT
    ),
    UvpmRetCode.INVALID_ISLANDS : RetCodeMetadata(
        op_status=OperationStatus.ERROR
    ),
    UvpmRetCode.NO_SIUTABLE_DEVICE : RetCodeMetadata(
        op_status=OperationStatus.ERROR
    ),
    UvpmRetCode.NO_UVS : RetCodeMetadata(
        op_status=OperationStatus.WARNING
    ),
    UvpmRetCode.INVALID_INPUT : RetCodeMetadata(
        op_status=OperationStatus.ERROR
    ),
    UvpmRetCode.WARNING : RetCodeMetadata(
        op_status=OperationStatus.WARNING
    )
}


class GroupingMethod:
    MATERIAL = EnumValue('0', 'Material', Labels.GROUP_METHOD_MATERIAL_DESC)
    # SIMILARITY = EnumValue('1', 'Similarity', Labels.GROUP_METHOD_SIMILARITY_DESC)
    MESH = EnumValue('2', 'Mesh Part', Labels.GROUP_METHOD_MESH_DESC)
    OBJECT = EnumValue('3', 'Object', Labels.GROUP_METHOD_OBJECT_DESC)
    MANUAL = EnumValue('4', 'Grouping Scheme (Manual)', Labels.GROUP_METHOD_MANUAL_DESC)
    TILE = EnumValue('5', 'Tile', Labels.GROUP_METHOD_TILE_DESC)

    @classmethod
    def to_blend_items(cls):
        return (cls.MATERIAL.to_blend_item(),
                # cls.SIMILARITY.to_blend_item(),
                cls.MESH.to_blend_item(),
                cls.OBJECT.to_blend_item(),
                cls.TILE.to_blend_item(),
                cls.MANUAL.to_blend_item())

    @classmethod
    def auto_grouping_enabled(cls, g_method):
        return g_method != cls.MANUAL.code


class TexelDensityGroupPolicy:
    INDEPENDENT = EnumValue(
        '0',
        Labels.TEXEL_DENSITY_GROUP_POLICY_INDEPENDENT_NAME,
        Labels.TEXEL_DENSITY_GROUP_POLICY_INDEPENDENT_DESC)

    UNIFORM = EnumValue(
        '1',
        Labels.TEXEL_DENSITY_GROUP_POLICY_UNIFORM_NAME,
        Labels.TEXEL_DENSITY_GROUP_POLICY_UNIFORM_DESC)

    CUSTOM = EnumValue(
        '2',
        Labels.TEXEL_DENSITY_GROUP_POLICY_CUSTOM_NAME,
        Labels.TEXEL_DENSITY_GROUP_POLICY_CUSTOM_DESC)

    @classmethod
    def to_blend_items(cls):
        return (cls.INDEPENDENT.to_blend_item(), cls.UNIFORM.to_blend_item(), cls.CUSTOM.to_blend_item())

    @classmethod
    def to_blend_items_auto(cls):
        return (cls.INDEPENDENT.to_blend_item(), cls.UNIFORM.to_blend_item())

class GroupLayoutMode:
    AUTOMATIC = EnumValue('0', 'Automatic', Labels.GROUP_LAYOUT_MODE_AUTOMATIC_DESC)
    MANUAL = EnumValue('1', 'Manual', Labels.GROUP_LAYOUT_MODE_MANUAL_DESC)
    AUTOMATIC_HORI = EnumValue('2', 'Automatic (Horizontal)', Labels.GROUP_LAYOUT_MODE_AUTOMATIC_HORI_DESC)
    AUTOMATIC_VERT = EnumValue('3', 'Automatic (Vertical)', Labels.GROUP_LAYOUT_MODE_AUTOMATIC_VERT_DESC)

    @classmethod
    def to_blend_items(cls):
        return\
            (cls.AUTOMATIC.to_blend_item(),
             cls.AUTOMATIC_HORI.to_blend_item(),
             cls.AUTOMATIC_VERT.to_blend_item(),
             cls.MANUAL.to_blend_item())

    @classmethod
    def to_blend_items_auto(cls):
        return (mode.to_blend_item() for mode in cls.automatic_modes())

    @classmethod
    def automatic_modes(cls):
        return\
            (cls.AUTOMATIC,
             cls.AUTOMATIC_HORI,
             cls.AUTOMATIC_VERT)

    @classmethod
    def is_automatic(cls, mode_code):
        return mode_code in (mode.code for mode in cls.automatic_modes())

    @classmethod
    def supports_tiles_in_row(cls, mode_code):
        return\
            mode_code == cls.AUTOMATIC.code

    @classmethod
    def supports_tile_count(cls, mode_code):
        return cls.is_automatic(mode_code)


class RunScenario:
    _SCENARIOS = {}

    @classmethod
    def add_scenario(cls, scenario):
        cls._SCENARIOS[scenario['id']] = scenario

    @classmethod
    def get_scenario(cls, scenario_id, default=None):
        return cls._SCENARIOS.get(scenario_id, default)
