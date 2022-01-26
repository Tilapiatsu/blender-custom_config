
from .utils import ShadowedPropertyGroupMeta, ShadowedPropertyGroup
from .enums import GroupLayoutMode, TexelDensityGroupPolicy
from .labels import Labels
from .box import mark_boxes_dirty
from .box_utils import disable_box_rendering

import bpy
from bpy.props import (IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty,
                       PointerProperty, FloatVectorProperty)



class UVPM3_GroupBase(ShadowedPropertyGroup):
    pass


class UVPM3_GroupingOptionsBase(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    TILES_IN_ROW_DEFAULT = 10
    LAST_GROUP_COMPLEMENTARY_DEFAULT = False
    GROUP_COMPACTNESS_DEFAULT = 0.0

    tiles_in_row : IntProperty(
        name=Labels.TILES_IN_ROW_NAME,
        default=TILES_IN_ROW_DEFAULT,
        min=1,
        max=100)

    last_group_complementary : BoolProperty(
        name=Labels.LAST_GROUP_COMPLEMENTARY_NAME,
        description=Labels.LAST_GROUP_COMPLEMENTARY_DESC,
        default=LAST_GROUP_COMPLEMENTARY_DEFAULT,
        update=mark_boxes_dirty)

    group_compactness : FloatProperty(
        name=Labels.GROUP_COMPACTNESS_NAME,
        description=Labels.GROUP_COMPACTNESS_DESC,
        default=GROUP_COMPACTNESS_DEFAULT,
        min=0.0,
        max=1.0,
        precision=2,
        step=10.0)

    def __init__(self):

        self.tiles_in_row = self.TILES_IN_ROW_DEFAULT
        self.last_group_complementary = self.LAST_GROUP_COMPLEMENTARY_DEFAULT
        self.group_compactness = self.GROUP_COMPACTNESS_DEFAULT

    def copy_from(self, other):

        self.tiles_in_row = int(other.tiles_in_row)
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


class UVPM3_AutoGroupingOptions(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    automatic : BoolProperty(name='', default=True)
    base : PointerProperty(type=UVPM3_GroupingOptionsBase)

    tdensity_policy : EnumProperty(
        items=TexelDensityGroupPolicy.to_blend_items_auto(),
        name=Labels.TEXEL_DENSITY_GROUP_POLICY_NAME,
        description=Labels.TEXEL_DENSITY_GROUP_POLICY_DESC)

    group_layout_mode : EnumProperty(
        items=GroupLayoutMode.to_blend_items(),
        name=Labels.GROUP_LAYOUT_MODE_NAME,
        description=Labels.GROUP_LAYOUT_MODE_DESC)
