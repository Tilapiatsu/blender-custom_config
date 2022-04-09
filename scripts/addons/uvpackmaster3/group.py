from .box import UVPM3_Box, mark_boxes_dirty
from .utils import ShadowedPropertyGroupMeta, ShadowedCollectionProperty
from .island_params import GroupIParamInfoGeneric
from .labels import Labels, PropConstants
from .grouping import UVPM3_GroupBase


import bpy
from bpy.props import (IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty,
                       PointerProperty, FloatVectorProperty)



def _update_group_info_name(self, context):
    if self.name.strip() == '':
        name = UVPM3_GroupInfo.get_default_group_name(self.num)
        self['name'] = name
    mark_boxes_dirty(self, context)


class UVPM3_GroupOverrides(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    OVERRIDE_PROPERTY_DEFAULT = False

    override_global_options : BoolProperty(
        name=Labels.OVERRIDE_GLOBAL_OPTIONS_NAME,
        description=Labels.OVERRIDE_GLOBAL_OPTIONS_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)


    override_rotation_enable : BoolProperty(
        name='Override {}'.format(Labels.ROTATION_ENABLE_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    rotation_enable : BoolProperty(
        name=Labels.ROTATION_ENABLE_NAME,
        description=Labels.ROTATION_ENABLE_DESC,
        default=PropConstants.ROTATION_ENABLE_DEFAULT)

    override_pre_rotation_disable : BoolProperty(
        name='Override {}'.format(Labels.PRE_ROTATION_DISABLE_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    pre_rotation_disable : BoolProperty(
        name=Labels.PRE_ROTATION_DISABLE_NAME,
        description=Labels.PRE_ROTATION_DISABLE_DESC,
        default=PropConstants.PRE_ROTATION_DISABLE_DEFAULT)

    override_rotation_step : BoolProperty(
        name='Override {}'.format(Labels.ROTATION_STEP_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    rotation_step : IntProperty(
        name=Labels.ROTATION_STEP_NAME,
        description=Labels.ROTATION_STEP_DESC,
        default=PropConstants.ROTATION_STEP_DEFAULT,
        min=PropConstants.ROTATION_STEP_MIN,
        max=PropConstants.ROTATION_STEP_MAX)

    override_pixel_margin : BoolProperty(
        name='Override {}'.format(Labels.PIXEL_MARGIN_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    pixel_margin : IntProperty(
        name=Labels.PIXEL_MARGIN_NAME,
        description=Labels.PIXEL_MARGIN_DESC,
        min=PropConstants.PIXEL_MARGIN_MIN,
        max=PropConstants.PIXEL_MARGIN_MAX,
        default=PropConstants.PIXEL_MARGIN_DEFAULT)

    override_pixel_padding : BoolProperty(
        name='Override {}'.format(Labels.PIXEL_PADDING_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    pixel_padding : IntProperty(
        name=Labels.PIXEL_PADDING_NAME,
        description=Labels.PIXEL_PADDING_DESC,
        min=PropConstants.PIXEL_PADDING_MIN,
        max=PropConstants.PIXEL_PADDING_MAX,
        default=PropConstants.PIXEL_PADDING_DEFAULT)

    override_extra_pixel_margin_to_others : BoolProperty(
        name='Override {}'.format(Labels.EXTRA_PIXEL_MARGIN_TO_OTHERS_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    extra_pixel_margin_to_others : IntProperty(
        name=Labels.EXTRA_PIXEL_MARGIN_TO_OTHERS_NAME,
        description=Labels.EXTRA_PIXEL_MARGIN_TO_OTHERS_DESC,
        min=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_MIN,
        max=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_MAX,
        default=PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_DEFAULT)

    override_pixel_margin_tex_size : BoolProperty(
        name='Override {}'.format(Labels.PIXEL_MARGIN_TEX_SIZE_NAME),
        description=Labels.OVERRIDE_GLOBAL_OPTION_DESC,
        default=OVERRIDE_PROPERTY_DEFAULT)

    pixel_margin_tex_size : IntProperty(
        name=Labels.PIXEL_MARGIN_TEX_SIZE_NAME,
        description=Labels.PIXEL_MARGIN_TEX_SIZE_DESC,
        min=PropConstants.PIXEL_MARGIN_TEX_SIZE_MIN,
        max=PropConstants.PIXEL_MARGIN_TEX_SIZE_MAX,
        default=PropConstants.PIXEL_MARGIN_TEX_SIZE_DEFAULT)

    def __init__(self, name=None, num=None):

        self.override_global_options = self.OVERRIDE_PROPERTY_DEFAULT

        self.override_rotation_enable = self.OVERRIDE_PROPERTY_DEFAULT 
        self.rotation_enable = PropConstants.ROTATION_ENABLE_DEFAULT

        self.override_pre_rotation_disable = self.OVERRIDE_PROPERTY_DEFAULT 
        self.pre_rotation_disable = PropConstants.PRE_ROTATION_DISABLE_DEFAULT

        self.override_rotation_step = self.OVERRIDE_PROPERTY_DEFAULT 
        self.rotation_step = PropConstants.ROTATION_STEP_DEFAULT

        self.override_pixel_margin = self.OVERRIDE_PROPERTY_DEFAULT
        self.pixel_margin = PropConstants.PIXEL_MARGIN_DEFAULT

        self.override_pixel_padding = self.OVERRIDE_PROPERTY_DEFAULT
        self.pixel_padding = PropConstants.PIXEL_PADDING_DEFAULT

        self.override_extra_pixel_margin_to_others = self.OVERRIDE_PROPERTY_DEFAULT
        self.extra_pixel_margin_to_others = PropConstants.EXTRA_PIXEL_MARGIN_TO_OTHERS_DEFAULT

        self.override_pixel_margin_tex_size = self.OVERRIDE_PROPERTY_DEFAULT
        self.pixel_margin_tex_size = PropConstants.PIXEL_MARGIN_TEX_SIZE_DEFAULT

    def copy_from(self, other):

        self.override_global_options = bool(other.override_global_options)

        self.override_rotation_enable = bool(other.override_rotation_enable)
        self.rotation_enable = int(other.rotation_enable)

        self.override_pre_rotation_disable = bool(other.override_pre_rotation_disable)
        self.pre_rotation_disable = int(other.pre_rotation_disable)

        self.override_rotation_step = bool(other.override_rotation_step)
        self.rotation_step = int(other.rotation_step)

        self.override_pixel_margin = bool(other.override_pixel_margin)
        self.pixel_margin = int(other.pixel_margin)

        self.override_pixel_padding = bool(other.override_pixel_padding)
        self.pixel_padding = int(other.pixel_padding)

        self.override_extra_pixel_margin_to_others = bool(other.override_extra_pixel_margin_to_others)
        self.extra_pixel_margin_to_others = int(other.extra_pixel_margin_to_others)

        self.override_pixel_margin_tex_size = bool(other.override_pixel_margin_tex_size)
        self.pixel_margin_tex_size = int(other.pixel_margin_tex_size)

        

class UVPM3_GroupInfo(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    DEFAULT_GROUP_NAME = 'G'

    @classmethod
    def get_default_group_name(cls, g_num):
        return "{}{}".format(cls.DEFAULT_GROUP_NAME, g_num)


    name : StringProperty(name="Name", default="", update=_update_group_info_name)
    num : IntProperty(name="Group Number", default=0)
    color : FloatVectorProperty(name="", default=(1.0, 1.0, 0.0), min=0.0, max=1.0, subtype="COLOR", update=mark_boxes_dirty)
    target_boxes : CollectionProperty(type=UVPM3_Box)
    active_target_box_idx : IntProperty(name="", default=0, update=mark_boxes_dirty)

    TDENSITY_CLUSTER_DEFAULT = 0
    tdensity_cluster : IntProperty(
        name=Labels.TEXEL_DENSITY_CLUSTER_NAME,
        description=Labels.TEXEL_DENSITY_CLUSTER_DESC ,
        default=TDENSITY_CLUSTER_DEFAULT,
        min=0)

    TILE_COUNT_DEFAULT = 1
    tile_count : IntProperty(
        name=Labels.TILE_COUNT_NAME,
        description=Labels.TILE_COUNT_DESC,
        default=TILE_COUNT_DEFAULT,
        min=1,
        max=100)

    overrides : PointerProperty(type=UVPM3_GroupOverrides)

    def __init__(self, name=None, num=None):

        self.name = name
        self.num = num
        self.color = GroupIParamInfoGeneric.GROUP_COLORS[self.num % len(GroupIParamInfoGeneric.GROUP_COLORS)] if self.num is not None else None
        self.active_target_box_idx = 0

        self.tdensity_cluster = self.TDENSITY_CLUSTER_DEFAULT
        self.tile_count = self.TILE_COUNT_DEFAULT

        self.target_boxes = ShadowedCollectionProperty(elem_type=UVPM3_Box)
        self.overrides = UVPM3_GroupOverrides()

    def copy_from(self, other):

        self.name = str(other.name)
        self.num = int(other.num)
        self.color = other.color[:]

        self.active_target_box_idx = int(other.active_target_box_idx)
        self.tdensity_cluster = int(other.tdensity_cluster)
        self.tile_count = int(other.tile_count)

        self.target_boxes.clear()
        for other_box in other.target_boxes:
            new_box = self.target_boxes.add()
            new_box.copy_from(other_box)

        self.overrides.copy_from(other.overrides)

    def is_default(self):
        return self.num == 0

    def add_target_box(self, new_box):

        added_box = self.target_boxes.add()
        added_box.copy_from(new_box)
        self.active_target_box_idx = len(self.target_boxes)-1

    def remove_target_box(self, box_idx):

        if len(self.target_boxes) <= 1:
            raise RuntimeError('Group has to have at least one target box')

        self.target_boxes.remove(box_idx)
        self.active_target_box_idx = min(self.active_target_box_idx, len(self.target_boxes)-1)

    def get_active_target_box(self):

        try:
            return self.target_boxes[self.active_target_box_idx]

        except IndexError:
            return None