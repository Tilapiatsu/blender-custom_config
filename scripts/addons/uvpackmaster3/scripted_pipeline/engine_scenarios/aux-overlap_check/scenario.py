from scripted_pipeline import GenericScenario
from uvpm_core import packer, RetCode, LogType, overlapping_islands, IslandFlag
from utils import flag_islands


class Scenario(GenericScenario):

    def run(self):

        islands_to_check = self.cx.selected_islands
        overlapping = overlapping_islands(islands_to_check, islands_to_check)[0]
        overlapping.set_flags(IslandFlag.OVERLAPS)

        flag_islands(islands_to_check, overlapping)

        if len(overlapping) > 0:
            log_type = LogType.WARNING
            log_msg = 'Overlapping islands detected (check selected islands)'
        else:
            log_type = LogType.INFO
            log_msg = 'No overlapping islands detected'

        packer.send_log(log_type, log_msg)
        packer.send_log(LogType.STATUS, 'Done')
        return RetCode.SUCCESS
