import uuid

from .box import DEFAULT_TARGET_BOX, mark_boxes_dirty
from .utils import ShadowedPropertyGroupMeta, ShadowedCollectionProperty, unique_name, unique_min_num
from .enums import GroupLayoutMode, TexelDensityGroupPolicy, GroupingMethod
from .group_map import *
from .island_params import IParamSerializer, IParamInfo
from .grouping import UVPM3_GroupBase, UVPM3_GroupingOptions
from .group import UVPM3_GroupInfo


import bpy
from bpy.props import (IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty, CollectionProperty,
                       PointerProperty, FloatVectorProperty)


def _update_grouping_scheme_name(self, context):
    scene_props = context.scene.uvpm3_props
    grouping_schemes = scene_props.grouping_schemes
    if self.name.strip() == '':
        name = UVPM3_GroupingScheme.DEFAULT_GROUPING_SCHEME_NAME
    else:
        name = self.name
    self['name'] = unique_name(name, grouping_schemes, self)


class UVPM3_GroupingScheme(UVPM3_GroupBase, metaclass=ShadowedPropertyGroupMeta):

    MIN_GROUP_NUM = 0
    MAX_GROUP_NUM = 100
    DEFAULT_GROUP_NUM = MIN_GROUP_NUM

    DEFAULT_GROUPING_SCHEME_NAME = 'Scheme'

    name : StringProperty(name="name", default="", update=_update_grouping_scheme_name)
    uuid : StringProperty(name="uuid", default="")
    groups : CollectionProperty(type=UVPM3_GroupInfo)
    active_group_idx : IntProperty(name="", default=0, update=mark_boxes_dirty)
    options : PointerProperty(type=UVPM3_GroupingOptions)

    @staticmethod
    def uuid_is_valid(uuid_to_test):
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=4)
        except ValueError:
            return False
        return uuid_obj.hex == uuid_to_test

    @staticmethod
    def uuid_generate():
        return uuid.uuid4().hex

    def __init__(self, _name='', _uuid=''):

        self.name = _name
        self.uuid = _uuid
        self.groups = ShadowedCollectionProperty(elem_type=UVPM3_GroupInfo)
        self.active_group_idx = 0
        self.options = UVPM3_GroupingOptions()

        self.init_defaults()

    def init_defaults(self):

        if self.name == '':
            self.name = self.DEFAULT_GROUPING_SCHEME_NAME

        if self.uuid == '':
            self.uuid = self.uuid_generate()

        self.group_by_name = dict()
        self.group_by_num = dict()
        self.group_map = None
        self.next_group_num = self.DEFAULT_GROUP_NUM

        for group in self.groups:
            self.__add_group_to_dictionaries(group)

    def regenerate_uuid(self):
        self.uuid = self.uuid_generate()

    def copy_from(self, other):

        self.name = str(other.name)
        self.uuid = str(other.uuid)

        self.clear_groups()
        for other_group in other.groups:
            self.add_group_internal(other_group)

        self.active_group_idx = int(other.active_group_idx)
        self.options.copy_from(other.options)
        self.init_defaults()

    def copy(self):

        out = UVPM3_GroupingScheme()
        out.copy_from(self)
        return out

    def clear_groups(self):

        self.groups.clear()
        self.group_by_name = dict()
        self.group_by_num = dict()
        self.group_map = None
        self.next_group_num = self.DEFAULT_GROUP_NUM

    def group_count(self):

        return len(self.groups)

    def complementary_group_supported(self):

        return self.options.tdensity_policy == TexelDensityGroupPolicy.UNIFORM.code and len(self.groups) > 1

    def complementary_group_enabled(self):

        return self.complementary_group_supported() and self.options.base.last_group_complementary

    def complementary_group(self):

        assert(self.complementary_group_enabled())
        assert(len(self.groups) > 0)
        return self.groups[len(self.groups)-1]

    def is_complementary_group(self, group):

        return self.complementary_group_enabled() and group.num == self.complementary_group().num

    def complementary_group_is_active(self):

        active_group = self.get_active_group()
        if active_group is None:
            return False
        return self.is_complementary_group(active_group)

    def apply_tdensity_policy(self):

        if self.options.tdensity_policy == TexelDensityGroupPolicy.CUSTOM.code:
            return

        for g_num, group in self.group_by_num.items():
            if self.options.tdensity_policy == TexelDensityGroupPolicy.INDEPENDENT.code:
                group.tdensity_cluster = g_num

            elif self.options.tdensity_policy == TexelDensityGroupPolicy.UNIFORM.code:
                group.tdensity_cluster = 0

            else:
                assert(False)

    def group_target_box_editing(self):
        return self.options.group_layout_mode == GroupLayoutMode.MANUAL.code

    def apply_group_layout(self):

        if self.group_target_box_editing():
            pass
        
        else:
            if self.options.group_layout_mode == GroupLayoutMode.AUTOMATIC.code:
                def box_func(group_idx, tile_idx, global_tile_idx):
                    return DEFAULT_TARGET_BOX.tile_from_num(global_tile_idx, self.options.base.tiles_in_row)
            elif self.options.group_layout_mode == GroupLayoutMode.AUTOMATIC_HORI.code:
                def box_func(group_idx, tile_idx, global_tile_idx):
                    return DEFAULT_TARGET_BOX.tile(tile_idx, group_idx)
            elif self.options.group_layout_mode == GroupLayoutMode.AUTOMATIC_VERT.code:
                def box_func(group_idx, tile_idx, global_tile_idx):
                    return DEFAULT_TARGET_BOX.tile(group_idx, tile_idx)
            else:
                assert False           

            global_tile_idx = 0
            for group_idx, group in enumerate(self.groups):
                group.target_boxes.clear()

                for tile_idx in range(group.tile_count):
                    new_box = group.target_boxes.add()
                    new_box.copy_from(box_func(group_idx, tile_idx, global_tile_idx))
                    global_tile_idx += 1

        if self.complementary_group_enabled():
            last_group = self.groups[-1]
            last_group.target_boxes.clear()

            for i in range(len(self.groups) - 1):
                group = self.groups[i]

                for box in group.target_boxes:
                    new_box = last_group.target_boxes.add()
                    new_box.copy_from(box)


    def get_group_by_name(self, g_name):

        group = self.group_by_name.get(g_name)

        if group is None:
            group = self.add_group_with_target_box(g_name)

        return group

    def get_group_by_num(self, g_num):

        group = self.group_by_num.get(g_num)
        return group

    def get_default_group(self):

        default_group = self.get_group_by_num(self.DEFAULT_GROUP_NUM)

        if default_group is None:
            default_group = self.add_group_with_target_box(g_num=self.DEFAULT_GROUP_NUM)

        return default_group

    def __add_group_to_dictionaries(self, group):

        if self.next_group_num <= group.num:
            self.next_group_num = group.num + 1

        self.group_by_name[group.name] = group
        self.group_by_num[group.num] = group

    def add_group(self, g_name=UVPM3_GroupInfo.DEFAULT_GROUP_NAME, g_num=None):

        if g_num is None:
            g_num = self.next_group_num

        if g_name == UVPM3_GroupInfo.DEFAULT_GROUP_NAME:
            g_name = UVPM3_GroupInfo.get_default_group_name(g_num)

        new_group = UVPM3_GroupInfo(g_name, g_num)
        return self.add_group_internal(new_group)

    def add_group_with_target_box(self, g_name=UVPM3_GroupInfo.DEFAULT_GROUP_NAME, g_num=None):

        new_group = self.add_group(g_name, g_num)
        self.add_target_box(new_group)

        return new_group

    def add_group_internal(self, new_group):

        added_group = self.groups.add()
        added_group.copy_from(new_group)
        self.options.group_initializer(added_group)
        
        self.__add_group_to_dictionaries(added_group)
        self.active_group_idx = len(self.groups)-1
        return added_group

    def group_to_text(self, g_num):

        group = self.get_group_by_num(g_num)

        if group is None:
            raise RuntimeError('Group not found')

        return group.name

    def group_to_color(self, g_num):

        group = self.get_group_by_num(g_num)

        if group is None:
            raise RuntimeError('Group not found')

        return group.color

    def remove_group(self, group_idx):

        group_to_remove = self.groups[group_idx]

        if group_to_remove.is_default():
            raise RuntimeError("Cannot remove the default group")

        del self.group_by_name[group_to_remove.name]
        del self.group_by_num[group_to_remove.num]

        self.groups.remove(group_idx)
        self.active_group_idx = min(self.active_group_idx, len(self.groups)-1)

    def box_intersects_group_boxes(self, box_to_check):

        for group in self.groups:
            if self.is_complementary_group(group):
                continue
            
            for box in group.target_boxes:
                if box.intersects(box_to_check):
                    return True

        return False

    def add_target_box(self, target_group):

        tile_num_x = 0
        tile_num_y = 0

        if len(target_group.target_boxes) > 0:
            min_corner = target_group.target_boxes[-1].min_corner
            tile_num_x = int(min_corner[0]) + 1
            tile_num_y = int(min_corner[1])

        while True:
            intersects = False
            new_box = DEFAULT_TARGET_BOX.tile(tile_num_x, tile_num_y)

            if not self.box_intersects_group_boxes(new_box):
                target_group.add_target_box(new_box)
                break

            tile_num_x += 1


    def init_group_map(self, p_context, g_method):

        g_method_to_map_type = {
            GroupingMethod.MATERIAL.code : GroupMapMaterial,
            GroupingMethod.MESH.code : GroupMapMeshPart,
            GroupingMethod.OBJECT.code : GroupMapObject,
            GroupingMethod.TILE.code : GroupMapTile,
            GroupingMethod.MANUAL.code : GroupMapManual
        }

        map_type = g_method_to_map_type[g_method]
        if map_type is None:
            raise RuntimeError('Unexpected grouping method encountered')

        self.group_map = map_type(self, p_context)
        return self.group_map


    def get_iparam_info(self):

        iparam_info = IParamInfo(
            script_name='g_scheme_{}'.format(self.uuid),
            label=self.group_map.iparam_label() if self.group_map is not None else 'Group',
            min_value=self.MIN_GROUP_NUM,
            max_value=self.MAX_GROUP_NUM
        )

        return iparam_info

    def get_active_group(self):

        try:
            return self.groups[self.active_group_idx]
        except IndexError:
            return None

    def is_valid(self):
        
        if self.name.strip() == '':
            return False

        if not self.uuid_is_valid(self.uuid):
            return False

        if len(self.groups) == 0:
            return False

        if self.active_group_idx not in range(len(self.groups)):
            return False

        def_group_found = False
        g_number_set = set()

        for group in self.groups:
            if group.name.strip() == '':
                return False

            if group.is_default():
                if def_group_found:
                    return False
                def_group_found = True

            if len(group.target_boxes) == 0:
                return False

            if group.active_target_box_idx not in range(len(group.target_boxes)):
                return False

            g_number_set.add(group.num)

        if not def_group_found:
            return False

        if len(g_number_set) != len(self.groups):
            return False

        return True


class GroupingSchemeSerializer(IParamSerializer):

    def __init__(self, g_scheme):
        super().__init__(g_scheme.get_iparam_info())

        self.g_scheme = g_scheme

    def serialize_iparam(self, p_obj_idx, p_obj, face):
        
        self.iparam_values.append(self.g_scheme.group_map.get_map(p_obj, face.index))


class GroupingSchemeAccess:

    def init_access(self, context, ui_drawing=False):
        self.context = context
        self.ui_drawing = ui_drawing
        self.init_active_members()

    def init_active_members(self):
        self.active_g_scheme = self.get_active_grouping_scheme()

        if not self.ui_drawing and self.active_g_scheme is not None:
            self.active_g_scheme.init_defaults()

        self.active_group = self.get_active_group()
        self.active_target_box = self.get_active_target_box()

    def get_grouping_schemes(self):
        return self.context.scene.uvpm3_props.grouping_schemes

    def get_grouping_schemes_enum_items(self):
        items = []
        grouping_schemes = self.get_grouping_schemes()
        enumerated_grouping_schemes = list(enumerate(grouping_schemes))
        enumerated_grouping_schemes.sort(key=lambda i: i[1].name)

        for idx, grouping_scheme in enumerated_grouping_schemes:
            items.append((str(idx), grouping_scheme.name, "", idx))
        return items

    @staticmethod
    def get_grouping_schemes_enum_items_callback(property_self, context):
        g_scheme_access = GroupingSchemeAccess()
        g_scheme_access.init_access(context, ui_drawing=True)
        return g_scheme_access.get_grouping_schemes_enum_items()

    def create_grouping_scheme(self, set_active=True):
        grouping_schemes = self.get_grouping_schemes()

        new_grouping_scheme = grouping_schemes.add()
        new_grouping_scheme.init_defaults()
        new_grouping_scheme.add_group_with_target_box()
        if set_active:
            self.set_active_grouping_scheme_idx(len(grouping_schemes)-1)

    def get_active_grouping_scheme_idx(self):
        return self.context.scene.uvpm3_props.active_grouping_scheme_idx

    def get_active_grouping_scheme(self):
        grouping_schemes = self.get_grouping_schemes()
        active_grouping_scheme_idx = self.context.scene.uvpm3_props.active_grouping_scheme_idx
        active_grouping_scheme = None

        if len(grouping_schemes) and active_grouping_scheme_idx < len(grouping_schemes):
            active_grouping_scheme = grouping_schemes[active_grouping_scheme_idx]

        return active_grouping_scheme

    def get_active_group(self):
        g_scheme = self.get_active_grouping_scheme()

        if g_scheme is None:
            return None

        return g_scheme.get_active_group()

    def get_active_target_box(self):

        group = self.get_active_group()

        if group is None:
            return None

        return group.get_active_target_box()

    def set_active_grouping_scheme_idx(self, idx):
        self.context.scene.uvpm3_props.active_grouping_scheme_idx = idx
        self.init_active_members()

    def impl_active_box(self):
        
        return self.active_target_box


class UVPM3_OT_GroupingSchemeOperatorGeneric(bpy.types.Operator, GroupingSchemeAccess):

    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):

        try:     
            self.init_access(context)
            return self.execute_impl(context)

        except Exception as ex:
            self.report({'ERROR'}, str(ex))

        return {'CANCELLED'}


class UVPM3_OT_NewGroupingScheme(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.new_grouping_scheme"
    bl_label = "New Grouping Scheme"

    def execute_impl(self, context):
        self.create_grouping_scheme()
        return {'FINISHED'}


class UVPM3_OT_RemoveGroupingScheme(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.remove_grouping_scheme"
    bl_label = "Remove"

    def execute_impl(self, context):
        grouping_schemes = self.get_grouping_schemes()
        active_idx = self.get_active_grouping_scheme_idx()

        if active_idx < 0:
            return {'CANCELLED'}

        grouping_schemes.remove(active_idx)
        self.set_active_grouping_scheme_idx(min(active_idx, len(grouping_schemes)-1))

        return {'FINISHED'}


class UVPM3_OT_UnlinkGroupingScheme(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.unlink_grouping_scheme"
    bl_label = "Unlink"

    def execute_impl(self, context):
        self.set_active_grouping_scheme_idx(-1)
        return {'FINISHED'}


class UVPM3_OT_NewGroupInfo(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.new_group_info"
    bl_label = "New Item"

    active_grouping_scheme_idx : IntProperty()

    def execute_impl(self, context):
        
        if self.active_g_scheme is None:
            return {'CANCELLED'}

        new_group = self.active_g_scheme.add_group_with_target_box()

        # new_group = self.active_g_scheme.groups.add()
        # new_group.init_defaults([i.num for i in self.active_g_scheme.groups])
        # self.active_g_scheme.active_group_idx = len(self.active_g_scheme.groups)-1

        mark_boxes_dirty(self, context)
        return {'FINISHED'}


class UVPM3_OT_RemoveGroupInfo(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.remove_group_info"
    bl_label = "Remove"

    def execute_impl(self, context):

        if self.active_g_scheme is None:
            return {'CANCELLED'}

        self.active_g_scheme.remove_group(self.active_g_scheme.active_group_idx)

        # idx = self.active_g_scheme.active_group_idx
        # active_group = self.active_g_scheme.groups[idx]

        # if active_group.is_default():
        #     self.report({'ERROR'}, "Cannot remove the default group")
        #     return {'FINISHED'}

        # self.active_g_scheme.groups.remove(idx)
        # if idx >= len(self.active_g_scheme.groups):
        #     self.active_g_scheme.active_group_idx = len(self.active_g_scheme.groups)-1

        mark_boxes_dirty(self, context)
        return {'FINISHED'}


class UVPM3_OT_MoveGroupInfo(UVPM3_OT_GroupingSchemeOperatorGeneric):
    bl_idname = "uvpackmaster3.move_group_info"
    bl_label = "Move"
    bl_description = "Move the active group up/down in the list"

    direction : EnumProperty(items=[("UP", "Up", "", 0), ("DOWN", "Down", "", 1)])

    def execute_impl(self, context):
        if self.active_g_scheme is None:
            return {'CANCELLED'}

        old_idx = self.active_g_scheme.active_group_idx
        new_idx = old_idx
        if self.direction == "UP":
            if old_idx > 0:
                new_idx = old_idx - 1
        else:
            if old_idx < len(self.active_g_scheme.groups) - 1:
                new_idx = old_idx + 1
        self.active_g_scheme.groups.move(old_idx, new_idx)
        self.active_g_scheme.active_group_idx = new_idx
        return {'FINISHED'}

class UVPM3_OT_NewTargetBox(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.new_target_box"
    bl_label = "New Item"

    active_grouping_scheme_idx : IntProperty()

    def execute_impl(self, context):

        if self.active_g_scheme is None:
            return {'CANCELLED'}
        if self.active_group is None:
            return {'CANCELLED'}

        self.active_g_scheme.add_target_box(self.active_group)

        mark_boxes_dirty(self, context)
        return {'FINISHED'}


class UVPM3_OT_RemoveTargetBox(UVPM3_OT_GroupingSchemeOperatorGeneric):

    bl_idname = "uvpackmaster3.remove_target_box"
    bl_label = "Remove"

    def execute_impl(self, context):

        if self.active_group is None:
            return {'CANCELLED'}

        self.active_group.remove_target_box(self.active_group.active_target_box_idx)

        mark_boxes_dirty(self, context)
        return {'FINISHED'}

class UVPM3_OT_MoveTargetBox(UVPM3_OT_GroupingSchemeOperatorGeneric):
    bl_idname = "uvpackmaster3.move_target_box"
    bl_label = "Move"
    bl_description = "Move the active box up/down in the list"

    direction : EnumProperty(items=[("UP", "Up", "", 0), ("DOWN", "Down", "", 1)])

    def execute_impl(self, context):
        if self.active_group is None:
            return {'CANCELLED'}

        old_idx = self.active_group.active_target_box_idx
        new_idx = old_idx
        if self.direction == "UP":
            if old_idx > 0:
                new_idx = old_idx - 1
        else:
            if old_idx < len(self.active_group.target_boxes) - 1:
                new_idx = old_idx + 1
        self.active_group.target_boxes.move(old_idx, new_idx)
        self.active_group.active_target_box_idx = new_idx
        return {'FINISHED'}
