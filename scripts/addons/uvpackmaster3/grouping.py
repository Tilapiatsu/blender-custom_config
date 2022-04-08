
from .utils import ShadowedPropertyGroupMeta, ShadowedPropertyGroup
from .enums import GroupLayoutMode, TexelDensityGroupPolicy
from .labels import Labels, PropConstants
from .box import mark_boxes_dirty
from .box_utils import disable_box_rendering

import bpy
from bpy.props import (IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty,
                       PointerProperty, FloatVectorProperty)



class UVPM3_GroupBase(ShadowedPropertyGroup):
    pass


class UVPM3_GroupingOptionsBase(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    tiles_in_row : IntProperty(
        name=Labels.TILES_IN_ROW_NAME,
        description=Labels.TILES_IN_ROW_DESC,
        default=PropConstants.TILES_IN_ROW_DEFAULT,
        min=1,
        max=100)

    tile_count_per_group : IntProperty(
        name=Labels.TILE_COUNT_PER_GROUP_NAME,
        description=Labels.TILE_COUNT_PER_GROUP_DESC,
        default=PropConstants.TILE_COUNT_PER_GROUP_DEFAULT,
        min=1,
        max=100)

    last_group_complementary : BoolProperty(
        name=Labels.LAST_GROUP_COMPLEMENTARY_NAME,
        description=Labels.LAST_GROUP_COMPLEMENTARY_DESC,
        default=PropConstants.LAST_GROUP_COMPLEMENTARY_DEFAULT,
        update=mark_boxes_dirty)

    group_compactness : FloatProperty(
        name=Labels.GROUP_COMPACTNESS_NAME,
        description=Labels.GROUP_COMPACTNESS_DESC,
        default=PropConstants.GROUP_COMPACTNESS_DEFAULT,
        min=0.0,
        max=1.0,
        precision=2,
        step=10.0)

    def __init__(self):

        self.tiles_in_row = PropConstants.TILES_IN_ROW_DEFAULT
        self.tile_count_per_group = PropConstants.TILE_COUNT_PER_GROUP_DEFAULT
        self.last_group_complementary = PropConstants.LAST_GROUP_COMPLEMENTARY_DEFAULT
        self.group_compactness = PropConstants.GROUP_COMPACTNESS_DEFAULT

    def copy_from(self, other):

        self.tiles_in_row = int(other.tiles_in_row)
        self.tile_count_per_group = int(other.tile_count_per_group)
        self.last_group_complementary = bool(other.last_group_complementary)
        self.group_compactness = float(other.group_compactness)


class UVPM3_GroupingOptions(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    automatic : BoolProperty(name='', default=False)
    base : PointerProperty(type=UVPM3_GroupingOptionsBase)

    tdensity_policy : EnumProperty(
        items=TexelDensityGroupPolicy.to_blend_items(),
        name=Labels.TEXEL_DENSITY_GROUP_POLICY_NAME,
        description=Labels.TEXEL_DENSITY_GROUP_POLICY_DESC,
        update=mark_boxes_dirty)

    group_layout_mode : EnumProperty(
        items=GroupLayoutMode.to_blend_items(),
        name=Labels.GROUP_LAYOUT_MODE_NAME,
        description=Labels.GROUP_LAYOUT_MODE_DESC,
        update=disable_box_rendering)

    def __init__(self):

        self.base = UVPM3_GroupingOptionsBase()
        self.tdensity_policy = TexelDensityGroupPolicy.INDEPENDENT.code
        self.group_layout_mode = GroupLayoutMode.AUTOMATIC.code

    def copy_from(self, other):

        self.base.copy_from(other.base)
        self.tdensity_policy = str(other.tdensity_policy)
        self.group_layout_mode = str(other.group_layout_mode)

        self.group_initializer = other.group_initializer

    def group_initializer(self, group):
        pass


class UVPM3_AutoGroupingOptions(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    automatic : BoolProperty(name='', default=True)
    base : PointerProperty(type=UVPM3_GroupingOptionsBase)

    tdensity_policy : EnumProperty(
        items=TexelDensityGroupPolicy.to_blend_items_auto(),
        name=Labels.TEXEL_DENSITY_GROUP_POLICY_NAME,
        description=Labels.TEXEL_DENSITY_GROUP_POLICY_DESC)

    group_layout_mode : EnumProperty(
        items=GroupLayoutMode.to_blend_items_auto(),
        name=Labels.GROUP_LAYOUT_MODE_NAME,
        description=Labels.GROUP_LAYOUT_MODE_DESC)

    def group_initializer(self, group):
        group.tile_count = self.base.tile_count_per_group
