from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode, LogType, IslandSet
from utils import eprint


class SplitMetadata:
    def __init__(self):
        self.split_offset = 0
        self.processed = False


class Scenario(GenericScenario):

    def run(self):
        
        split_offset_iparam_name = self.cx.params['split_offset_iparam_name']
        split_offset_iparam_desc = self.iparams_manager.iparam_desc(split_offset_iparam_name)
        offset_step = 1

        for island in self.cx.selected_islands:
            island.metadata = SplitMetadata()

        processed = IslandSet()
        to_process = self.cx.selected_islands.clone()

        while len(to_process) > 0:
            to_check = to_process.clone()
            to_check += processed

            o_map = to_check.overlapping_map()
            # eprint(o_map)
            overlapping_islands = []
            for island in to_check:
                island.overlapping = o_map[island]

                if len(island.overlapping) == 0:
                    if not island.metadata.processed:
                        island.metadata.processed = True
                        processed.append(island)
                    continue

                if island.metadata.processed:
                    island.metadata.local_offset = 0
                    continue
            
                island.metadata.local_offset = None
                overlapping_islands.append(island)

            overlapping_islands.sort(key=lambda island: len(island.overlapping))
            to_process.clear()

            for island in overlapping_islands:

                free_offset = None
                offset_to_check = 0

                while True:
                    offset_found = True

                    for other_island in island.overlapping:
                        if other_island.metadata.local_offset is not None and other_island.metadata.local_offset == offset_to_check:
                            offset_found = False
                            break

                    if offset_found:
                        free_offset = offset_to_check
                        break

                    offset_to_check += offset_step

                # max_offset = max(max_offset, free_offset)
                island.metadata.local_offset = free_offset
                island.metadata.split_offset += free_offset

                if free_offset != 0:
                    to_process.append(island.offset(free_offset, 0.0))
                else:
                    to_process.append(island)

        assert(len(processed) == len(self.cx.selected_islands))

        moved_count = 0
        for island in processed:
            split_offset = island.metadata.split_offset

            if split_offset > 0:
                moved_count += 1

            island.set_iparam(split_offset_iparam_desc, split_offset)
            # if max_offset <= SplitOffsetParamInfo.MAX_VALUE:
            #     undo_possible = True
            #     for island in self.islands:
            #         island.set_param(SplitOffsetParamInfo, island.split_offset)

            # else:
            #     undo_possible = False
            #     for island in self.islands:
            #         island.set_param(SplitOffsetParamInfo, SplitOffsetParamInfo.INVALID_VALUE)
            
        split_offset_iparam_desc.mark_dirty()

        packer.send_out_islands(processed, send_transform=True, send_iparams=True)
        packer.send_log(LogType.STATUS, "Done. Islands moved: {}".format(moved_count))
        return RetCode.SUCCESS
