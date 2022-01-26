
from uvpm_core import (
    packer,
    RetCode,
    LogType,
    InputError,
    IslandSet,
    InvalidIslandsError,
    OpCancelledException
)
from utils import box_from_coords, eprint, flag_islands


def TO_ENUM(enum_type, value, default_value=None):
    if value is None:
        if default_value is not None:
            return default_value
        return enum_type.__DEFAULT
        
    return enum_type(value)


class GroupInfo:

    def __init__(self, name, num, tdensity_cluster, target_boxes):

        self.name = name
        self.num = num
        self.islands = None
        self.tdensity_cluster = tdensity_cluster
        self.target_boxes = target_boxes


class GroupingScheme:

    def __init__(self, in_g_scheme, group_iparam_desc):

        self.group_iparam_desc = group_iparam_desc
        self.group_compactness = in_g_scheme['group_compactness']
        self.groups = []
        self.groups_by_num = dict()

    def add_group(self, group):

        if self.groups_by_num.get(group.num) is not None:
            raise InputError('Duplicated group numbers in the grouping scheme')

        self.groups_by_num[group.num] = group
        self.groups.append(group)

    def assign_islands_to_groups(self, islands):

        islands_by_groups = islands.split_by_iparam(self.group_iparam_desc)

        for g_num, g_islands in islands_by_groups.items():

            group = self.groups_by_num.get(g_num)
            if group is None:
                raise InputError('Island assigned to an invalid group')

            group.islands = g_islands


class GenericScenario:

    GROUPING_SCHEME_PARAM_NAME = '__grouping_scheme'

    def __init__(self, cx):
        self.cx = cx
        self.iparams_manager = packer.std_iparams_manager()
        self.g_scheme = None

    def handle_invalid_topology(self, invalid_islands):

        flag_islands(self.cx.input_islands, invalid_islands)
        packer.send_log(LogType.STATUS, "Topology error")
        packer.send_log(LogType.ERROR, "Islands with invalid topology encountered (check the selected islands)")

    def parse_topology(self):

        invalid_islands = IslandSet()
        packer.parse_island_topology(self.cx.input_islands, invalid_islands)
        if len(invalid_islands) > 0:
            self.handle_invalid_topology(invalid_islands)
            raise InvalidIslandsError()

    def init(self):

        if not self.cx.params['__skip_topology_parsing']:
            self.parse_topology()

        in_g_scheme = self.cx.params[self.GROUPING_SCHEME_PARAM_NAME]

        if in_g_scheme is not None:

            group_iparam_desc = self.iparams_manager.iparam_desc(in_g_scheme['iparam_name'])
            if group_iparam_desc is None:
                raise InputError('Invalid island parameter passed in the grouping scheme')

            g_scheme = GroupingScheme(in_g_scheme, group_iparam_desc)

            for in_group in in_g_scheme['groups']:

                target_boxes = []
                for box_coords in in_group['target_boxes']:
                    target_boxes.append(box_from_coords(box_coords))

                group = GroupInfo(in_group['name'], in_group['num'], in_group['tdensity_cluster'], target_boxes)
                g_scheme.add_group(group)

            self.g_scheme = g_scheme

    def exec(self):

        ret_code = RetCode.NOT_SET
        try:
            self.init()
            self.pre_run()
            ret_code = self.run()
            self.post_run(ret_code)

        except InputError as err:
            packer.send_log(LogType.ERROR, str(err))
            packer.send_log(LogType.STATUS, 'Invalid operation input')
            return RetCode.INVALID_INPUT

        except InvalidIslandsError as err:
            return RetCode.INVALID_ISLANDS

        except OpCancelledException:
            return RetCode.CANCELLED

        return ret_code

    def pre_run(self):
        pass
    
    def post_run(self, ret_code):
        pass
