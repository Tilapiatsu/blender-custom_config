
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


class Struct(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap_str(self, value):
        return value

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        elif isinstance(value, dict):
            return Struct(value)
        elif isinstance(value, str):
            return self._wrap_str(value)
        else:
            return value


class GroupInfo(Struct):

    def __init__(self, in_group):
        super().__init__(in_group)

        self.islands = None
        self.target_boxes = []
        for box_coords in in_group['target_boxes']:
            self.target_boxes.append(box_from_coords(box_coords))



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

    def validate_locking(self):

        for group in self.groups:
            if group.islands is None:
                continue

            for island in group.islands:
                if island.parent_count < 2:
                    continue

                parents = island.parents
                parent_groups = set()
                for parent in parents:
                    parent_groups.add(parent.get_iparam(self.group_iparam_desc))

                    if len(parent_groups) > 1:
                        packer.send_log(LogType.WARNING, 'Islands from two different groups were locked together!')
                        packer.send_log(LogType.WARNING, 'In result some islands will be processed as not belonging to the groups they were originally assigned to')
                        return


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

    def islands_for_topology_parsing(self):
        return self.cx.input_islands

    def parse_topology(self):

        islands_for_parsing = self.islands_for_topology_parsing()
        invalid_islands = IslandSet()
        packer.parse_island_topology(islands_for_parsing, invalid_islands)
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
                

                # group = GroupInfo(
                #     in_group['name'],
                #     in_group['num'],
                #     in_group['tdensity_cluster'],
                #     in_group['rotation_step'],
                #     in_group['pixel_margin'],
                #     target_boxes)

                group = GroupInfo(in_group)
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
