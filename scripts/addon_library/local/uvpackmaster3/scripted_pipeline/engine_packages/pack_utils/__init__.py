from uvpm_core import (packer,
                     Box,
                     Point,
                     IslandSet,
                     PackRunConfig,
                     PackParams,
                     RetCode,
                     LockOverlappingMode,
                     LogType,
                     IslandFlag,
                     solution_available,
                     append_ret_codes,
                     raise_InvalidTopologyExtendedError)
from scripted_pipeline import TO_ENUM, GenericScenario
from similarity_utils import SimilarityScenario
from utils import flag_islands, box_from_coords, eprint, area_to_string

from .pack_manager import PackManager



OVERLAPPING_WARNING_MSG_ARRAY = [
    "Overlapping islands were detected after packing (check the selected islands).",
    "Consider increasing the 'Precision' parameter."
]

OUTSIDE_TARGET_BOX_WARNING_MSG = "Some islands are outside their target boxes after packing (check the selected islands)."
NO_SIUTABLE_DEVICE_STATUS_MSG = "No suitable packing device."

NO_SIUTABLE_DEVICE_ERROR_MSG_ARRAY = [
    "No suitable packing device to perform the operation.",
    "Make sure that you have at least one packing device enabled in Preferences."
]

CORRECT_VERTICES_WARNING_MSG_ARRAY = [
    "Similarity option Correct Vertices is ignored when packing with stack groups.",
    "Read stack groups documentation for more info."
]


def merge_overlapping_islands(input_islands, overlapping_mode, iparam_desc):

    if overlapping_mode == LockOverlappingMode.DISABLED and iparam_desc is None:
        return input_islands

    overlapping_groups, not_overlapping_islands = input_islands.split_by_overlapping(overlapping_mode, iparam_desc)
    output_islands = IslandSet()

    for group in overlapping_groups:
        output_islands.append(group.merge())

    output_islands += not_overlapping_islands
    return output_islands


class PackScenario(GenericScenario):

    def __init__(self, cx):
        super().__init__(cx)

        self.simi_scenario = None
        if 'simi_params' in self.cx.params:
            self.simi_scenario = SimilarityScenario(self.cx)

    def apply_pack_ratio_to_islands(self, islands):

        if self.pack_ratio == 1.0:
            return islands

        output = IslandSet()

        for island in islands:
            output.append(island.scale(self.pack_ratio, 1.0))

        return output

    def unapply_pack_ratio_from_islands(self, islands):

        if self.pack_ratio == 1.0:
            return islands

        output = IslandSet()

        for island in islands:
            output.append(island.scale(1.0 / self.pack_ratio, 1.0))

        return output

    def apply_pack_ratio_to_box(self, box):

        if self.pack_ratio == 1.0:
            return

        box.min_corner.x *= self.pack_ratio
        box.max_corner.x *= self.pack_ratio

    def send_out_islands(self, island_set_list, **kwargs):

        transform_kw = 'send_transform'
        if self.pack_ratio != 1.0 and (transform_kw in kwargs) and kwargs[transform_kw]:
            tmp_list = []

            for islands in island_set_list:
                if islands is None:
                    continue
                tmp_list.append(self.unapply_pack_ratio_from_islands(islands))

            island_set_list = tmp_list

        packer.send_out_islands(island_set_list, send_transform=True)

    def pre_run(self):

        if self.simi_scenario:
            self.simi_scenario.pre_run()

        self.pack_ratio = self.cx.params.get('__pack_ratio', 1.0)

        selected_islands = self.apply_pack_ratio_to_islands(self.cx.selected_islands)
        unselected_islands = self.apply_pack_ratio_to_islands(self.cx.unselected_islands)

        self.target_boxes = None
        in_target_boxes = self.cx.params['target_boxes']
        if in_target_boxes is not None:
            self.target_boxes = [box_from_coords(in_box) for in_box in in_target_boxes]

            for box in self.target_boxes:
                self.apply_pack_ratio_to_box(box)

        if self.g_scheme is not None:
            for group in self.g_scheme.groups:
                for box in group.target_boxes:
                    self.apply_pack_ratio_to_box(box)

        self.static_islands = unselected_islands if self.cx.params['pack_to_others'] else None

        self.pack_runconfig = PackRunConfig()
        self.pack_runconfig.asyn = True
        self.pack_runconfig.realtime_solution = True

        if 'heuristic_search_time' in self.cx.params:
            self.pack_runconfig.heuristic_search_time = self.cx.params['heuristic_search_time']
        if 'advanced_heuristic' in self.cx.params:
            self.pack_runconfig.advanced_heuristic = self.cx.params['advanced_heuristic']
        if 'heuristic_max_wait_time' in self.cx.params:
            self.pack_runconfig.heuristic_max_wait_time = self.cx.params['heuristic_max_wait_time']
                
        self.islands_to_pack = selected_islands

        lock_group_iparam_desc = None
        lock_group_iparam_name = self.cx.params['lock_group_iparam_name']
        if lock_group_iparam_name is not None:
            lock_group_iparam_desc = self.iparams_manager.iparam_desc(lock_group_iparam_name)

        if self.simi_scenario and self.simi_scenario.stack_group_iparam_desc:
            packer.send_log(LogType.STATUS, "Stack groups aligning...")

            if self.simi_scenario.is_vertex_based() and self.simi_scenario.simi_params.correct_vertices:
                for msg in CORRECT_VERTICES_WARNING_MSG_ARRAY:
                    packer.send_log(LogType.WARNING, msg)

                self.simi_scenario.simi_params.correct_vertices = False

            (aligned_groups, non_aligned_islands) = self.simi_scenario.align_similar_by_stack_group(self.islands_to_pack)

            lock_groups = None
            if lock_group_iparam_desc:
                lock_groups = self.islands_to_pack.split_by_iparam(lock_group_iparam_desc)
            else:
                # Use stack group iparam for lock group
                lock_group_iparam_desc = self.simi_scenario.stack_group_iparam_desc

            curr_lock_val = lock_group_iparam_desc.max_value
            for group in aligned_groups:
                while lock_groups and (curr_lock_val in lock_groups):
                    curr_lock_val -= 1
                    
                if curr_lock_val <= lock_group_iparam_desc.default_value:
                        raise RuntimeError('Not enough lock groups')

                for island in group:
                    island.set_iparam(lock_group_iparam_desc, curr_lock_val)
                curr_lock_val -= 1

            if lock_groups is None:
                for island in non_aligned_islands:
                    island.set_iparam(lock_group_iparam_desc, lock_group_iparam_desc.default_value)

            self.islands_to_pack = non_aligned_islands
            for group in aligned_groups:
                self.islands_to_pack += group
                    
        lock_overlapping_mode = TO_ENUM(LockOverlappingMode, self.cx.params['lock_overlapping_mode'], LockOverlappingMode.DISABLED)
        locking_enabled = (lock_overlapping_mode != LockOverlappingMode.DISABLED) or (lock_group_iparam_desc is not None)

        if locking_enabled:
            self.islands_to_pack = merge_overlapping_islands(self.islands_to_pack, lock_overlapping_mode, lock_group_iparam_desc)

        if self.cx.params['normalize_islands']:
            self.islands_to_pack = self.islands_to_pack.normalize()

        if self.g_scheme is not None:
            self.g_scheme.assign_islands_to_groups(self.islands_to_pack)

            if locking_enabled:
                self.g_scheme.validate_locking()
                            
        self.pack_params = PackParams(self.cx.params)

        rotation_step_iparam_name = self.cx.params['rotation_step_iparam_name']
        if rotation_step_iparam_name is not None:
            self.pack_params.rotation_step_iparam_desc = self.iparams_manager.iparam_desc(rotation_step_iparam_name)

        scale_limit_iparam_name = self.cx.params['scale_limit_iparam_name']
        if scale_limit_iparam_name is not None:
            self.pack_params.scale_limit_iparam_desc = self.iparams_manager.iparam_desc(scale_limit_iparam_name)

        self.pack_manager = PackManager(self, self.pack_runconfig)

    def post_run_island_sets(self):

        return [self.pack_manager.packed_islands], self.pack_manager.invalid_islands


    def post_run(self, ret_code):

        packed_islands_array, invalid_islands = self.post_run_island_sets()

        if ret_code == RetCode.NO_SIUTABLE_DEVICE:
            packer.send_log(LogType.STATUS, NO_SIUTABLE_DEVICE_STATUS_MSG)
            for msg in NO_SIUTABLE_DEVICE_ERROR_MSG_ARRAY:
                packer.send_log(LogType.ERROR, msg)
            return ret_code

        if ret_code == RetCode.INVALID_ISLANDS:
            assert len(invalid_islands) > 0
            raise_InvalidTopologyExtendedError(invalid_islands)

        if not solution_available(ret_code):
            return ret_code

        packed_islands_area = 0.0
        for packed_islands in packed_islands_array:
            packed_islands_area += packed_islands.area()

        if ret_code == RetCode.SUCCESS:
            packer.send_log(LogType.STATUS, 'Packing done')
            packer.send_log(LogType.INFO, 'Packed islands area: {}'.format(area_to_string(packed_islands_area)))

        elif ret_code == RetCode.NO_SPACE:
            packer.send_log(LogType.STATUS, 'Packing stopped - no space to pack all islands')
            packer.send_log(LogType.WARNING, 'No space to pack all islands')
            packer.send_log(LogType.WARNING, 'Overlap check was performed only on the islands which have been packed')
        
        else:
            assert(False)

        overlapping = IslandSet()

        for packed_islands in packed_islands_array:
            packed_overlapping = packed_islands.overlapping_islands(packed_islands)[0]
            packed_overlapping.set_flags(IslandFlag.OVERLAPS)
            overlapping += packed_overlapping

            if self.static_islands is not None:
                packed_static_overlapping = packed_islands.overlapping_islands(self.static_islands)[0]
                packed_static_overlapping.set_flags(IslandFlag.OVERLAPS)
                overlapping += packed_static_overlapping

        flagged_islands = overlapping
        flag_islands(self.cx.selected_islands, flagged_islands)

        if len(overlapping) > 0:
            for msg in OVERLAPPING_WARNING_MSG_ARRAY:
                packer.send_log(LogType.WARNING, msg)

            ret_code = append_ret_codes(ret_code, RetCode.WARNING)

        return ret_code
