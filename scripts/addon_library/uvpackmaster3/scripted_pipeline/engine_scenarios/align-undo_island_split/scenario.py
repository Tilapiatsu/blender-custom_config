from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode, LogType, IslandSet, InputError
from utils import eprint


class Scenario(GenericScenario):

    def run(self):
        
        split_offset_iparam_name = self.cx.params['split_offset_iparam_name']
        split_offset_iparam_desc = self.iparams_manager.iparam_desc(split_offset_iparam_name)

        processed = IslandSet()
        moved_count = 0

        for island in self.cx.selected_islands:

            split_offset = island.get_iparam(split_offset_iparam_desc)
            if split_offset < 0:
                raise InputError("Split data not available for all selected islands")

            if split_offset > 0:
                processed_island = island.offset(-split_offset, 0.0)
                moved_count += 1
            else:
                processed_island = island

            processed_island.set_iparam(split_offset_iparam_desc, split_offset_iparam_desc.default_value)
            processed.append(processed_island)
        
        split_offset_iparam_desc.mark_dirty()

        packer.send_out_islands(processed, send_transform=True, send_iparams=True)
        packer.send_log(LogType.STATUS, "Done. Islands moved: {}".format(moved_count))
        return RetCode.SUCCESS
